import logging
from datetime import date, datetime

# Configure logger for this module
logger = logging.getLogger(__name__)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST

from user_auth.models import Profiles
from .forms import (
    EstablishmentForm,
    InspectionForm,
    EstablishmentRegisterForm,
    EstablishmentLicenceForm,
    InspectionAssignmentForm,
)
from .models import (
    Establishment,
    ArduinoReader,
    EstablishmentLicence,
    EstablishmentRegister,
    InspectionAssignment,
    Inspection,
)
from .utils import (
    mark_inspection_as_done,
    get_establishment_obj_by_register,
)


@login_required(login_url="login")
def add_establishment(request):
    """
    Handles the creation of a new establishment.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the form template with appropriate context.
    """
    if request.method == "POST":
        form = EstablishmentForm(request.POST)
        if form.is_valid():
            establishment = form.save()
            logger.info(f"New establishment created: {establishment.establishment_name} (ID: {establishment.id})")
            messages.success(request, "تم إضافة المنشأة بنجاح")
            return redirect("view_establishment")
        logger.warning(f"Failed to create establishment: {form.errors}")
        messages.error(request, "حدث خطأ أثناء إضافة المنشأة")
    else:
        form = EstablishmentForm()

    return render(request, "licesnsing/add_establishment.html", {"form": form})


@login_required(login_url="login")
def dashboard(request):
    """
    Renders a dashboard with key statistics and latest records.
    
    Displays metrics including:
    - Total counts for establishments, assignments, licenses, and inspections
    - Assignment status distribution
    - Monthly inspection trends
    - Inspection status breakdown
    - Municipality and activity statistics
    - License status overview
    
    Returns:
        HttpResponse: Renders the dashboard template with statistics context.
    """
    from django.db.models.functions import TruncMonth
    from django.utils import timezone
    from datetime import timedelta

    logger.info(f"Dashboard accessed by user: {request.user.username}")
    
    # Basic statistics
    total_establishments = Establishment.objects.count()
    total_assignments = InspectionAssignment.objects.count()
    total_licenses = EstablishmentLicence.objects.count()
    total_inspections = Inspection.objects.count()

    # Assignment status distribution
    assignments_by_status = (
        InspectionAssignment.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    # Monthly inspections (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_inspections = (
        Inspection.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    # Inspection status distribution
    inspection_status = [
        {"status": True, "count": Inspection.objects.filter(status=True).count()},
        {"status": False, "count": Inspection.objects.filter(status=False).count()},
    ]

    # Top 5 municipalities
    municipality_stats = (
        Establishment.objects.values("municipality_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # Activity distribution (top 3)
    activity_stats = (
        Establishment.objects.values("activity__ar_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    # License status (active vs expired)
    today = timezone.now().date()
    active_licenses = EstablishmentLicence.objects.filter(
        expiration_date__gt=today
    ).count()
    expired_licenses = EstablishmentLicence.objects.filter(
        expiration_date__lte=today
    ).count()
    license_status = [
        {"status": "Active", "count": active_licenses},
        {"status": "Expired", "count": expired_licenses},
    ]

    context = {
        "total_establishments": total_establishments,
        "total_assignments": total_assignments,
        "total_licenses": total_licenses,
        "total_inspections": total_inspections,
        "assignments_by_status": assignments_by_status,
        "monthly_inspections": monthly_inspections,
        "inspection_status": inspection_status,
        "municipality_stats": municipality_stats,
        "activity_stats": activity_stats,
        "license_status": license_status,
    }
    return render(request, "licesnsing/index.html", context)


@login_required(login_url="login")
def view_establishment(request):
    """
    Displays a paginated list of all registered establishments.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the template with paginated establishments.
    """
    establishments = Establishment.objects.all().order_by("-id")

    paginator = Paginator(establishments, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    logger.info(f"User {request.user.username} viewed establishments list (page: {request.GET.get('page', 1)})")

    active_registers = EstablishmentRegister.objects.filter(expiration_date__gt=date.today()).count()
    active_licenses = EstablishmentLicence.objects.filter(expiration_date__gt=date.today()).count()
    expired_registers = EstablishmentRegister.objects.filter(expiration_date__lte=date.today()).count()
    expired_licenses = EstablishmentLicence.objects.filter(expiration_date__lte=date.today()).count()
    return render(
        request,
        "licesnsing/view_establishment.html",
        {
            "today": date.today(),
            "page_obj": page_obj,
            "active_registers": active_registers,
            "active_licenses": active_licenses,
            "expired_registers": expired_registers,
            "expired_licenses": expired_licenses
        },
    )


@login_required(login_url="login")
def delete_establishment(request, register_number):
    """
    Deletes an establishment based on the provided register number.

    Args:
        request (HttpRequest): The HTTP request object.
        register_number (str): The unique register number of the establishment.

    Returns:
        HttpResponse: Redirects to the establishment list view.
    """
    try:
        establishment = get_establishment_obj_by_register(register_number)
        establishment_name = establishment.establishment_name
        establishment.delete()
        logger.info(f"Establishment deleted: {establishment_name} (Register: {register_number}) by user {request.user.username}")
        messages.success(request, "تم حذف المنشأة بنجاح")
    except Establishment.DoesNotExist:
        logger.warning(f"Attempt to delete non-existent establishment with register number: {register_number} by user {request.user.username}")
        messages.error(request, "المنشأة غير موجودة")

    return redirect("view_establishment")


@login_required(login_url="login")
def edit_establishment(request, rifd):
    """
    Edits an existing establishment's details.

    Args:
        request (HttpRequest): The HTTP request object.
        rifd (str): The RFID of the establishment.

    Returns:
        HttpResponse: Renders the edit form with the establishment data.
    """
    establishment = get_object_or_404(Establishment, rifd=rifd)
    form = EstablishmentForm(request.POST or None, instance=establishment)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        logger.info(f"Establishment updated: {establishment.establishment_name} (RFID: {rifd}) by user {request.user.username}")
        messages.success(request, "تم تحديث المنشأة بنجاح")
        return redirect("view_establishment")

    return render(request, "licesnsing/edit_establishment.html", {"form": form})


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def query(request):
    """
    Checks for new unread entries from the Arduino device.
    
    Fetches the latest unread record from ArduinoReader and attempts to match
    it with an establishment. Returns appropriate JSON response based on the result.

    Returns:
        JsonResponse: Contains establishment data or not found message.
    """
    # Fetch the latest unread ArduinoReader entry
    code = (
        ArduinoReader.objects.filter(queried=False, status="pending")
        .order_by("-id")
        .first()
    )

    if not code:
        # No new unread record found
        logger.debug("No new Arduino reader entries found")
        return JsonResponse(
            {
                "found": False,
                "template": render(
                    request,
                    "licesnsing/query.html",
                    {"found": False},
                ).content.decode("utf-8"),
            }
        )

    # Look for an establishment with the corresponding RFID code
    establishment = Establishment.objects.filter(rifd=code.code).first()

    if establishment:
        # Mark the code as processed
        code.status = "processed"
        code.save()
        
        logger.info(f"RFID match found: {code.code} -> Establishment: {establishment.establishment_name}")
        
        # Return the establishment data
        return JsonResponse(
            {
                "found": True,
                "code": code.code,
                "template": render(
                    request,
                    "licesnsing/query.html",
                    {
                        "eform": EstablishmentForm(instance=establishment),
                        "datafound": True,
                        "iform": InspectionForm(),
                        "found": True,
                        "register_number": establishment.get_register.id,
                    },
                ).content.decode("utf-8"),
            }
        )

    # No matching establishment found
    logger.warning(f"No establishment found for RFID code: {code.code}")
    return JsonResponse(
        {
            "found": False,
            "template": render(
                request,
                "licesnsing/query.html",
                {"found": False},
            ).content.decode("utf-8"),
        }
    )


@login_required(login_url="login")
def reader(request):
    """
    Displays establishments assigned to the current user for inspection.
    
    Returns:
        HttpResponse: Renders the RFID reader template with assigned establishments.
    """
    establishments = [
        assignment
        for assignment in InspectionAssignment.objects.filter(
            inspector=request.user, status="pending"
        )
    ]
    
    if not establishments:
        logger.info(f"No pending inspections found for user: {request.user.username}")
        messages.warning(request, "لا توجد لديك منشآت جديدة للمعاينة.")

    return render(
        request, "licesnsing/readRFID.html", {"establishments": establishments}
    )


@login_required(login_url="login")
def inspect_establishment(request, id):
    """
    Handles the inspection of an establishment.
    
    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the establishment to inspect.
        
    Returns:
        HttpResponse: Renders the inspection form or redirects after submission.
    """
    establishment = get_object_or_404(Establishment, id=id)
    
    if request.method == "POST":
        form = InspectionForm(request.POST, request.FILES)
        register_number = request.POST.get("register_number")
        
        if form.is_valid():
            inspection = form.save()
            # Mark inspection as done
            mark_inspection_as_done(get_establishment_obj_by_register(register_number))
            logger.info(f"Inspection completed for establishment: {establishment.establishment_name} (ID: {id}) by user {request.user.username}")
            messages.success(request, "تم إرسال المعاينة بنجاح")
            return redirect("reader")
        else:
            logger.warning(f"Inspection form validation failed for establishment {id}: {form.errors}")
            messages.warning(request, "الرجاء تصحيح الأخطاء في النموذج.")
            messages.warning(request, form.errors.as_ul())
            return render(
                request,
                "licesnsing/query.html",
                {
                    "eform": EstablishmentForm(instance=establishment),
                    "iform": form,  # Return the form with errors
                    "found": True,
                    "register_number": establishment.get_register.id,
                },
            )
    
    # GET request - show the inspection form
    return  render(
                request,
                "licesnsing/query.html",
                {
                    "eform": EstablishmentForm(instance=establishment),
                    "establishment": establishment,
                    "datafound": True,
                    "iform": InspectionForm(),
                    "found": True,
                    "register_number": establishment.get_register.id,
                },
            )



@login_required(login_url="login")
def inspection_delete(request, id):
    """
    Deletes an inspection record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the inspection to delete.
        
    Returns:
        HttpResponse: Redirects to the inspection list view.
    """
    try:
        inspection = get_object_or_404(Inspection, id=id)
        inspection.delete()
        logger.info(f"Inspection deleted: ID {id} by user {request.user.username}")
        messages.success(request, "تم حذف المعاينة بنجاح")
    except Exception as e:
        logger.error(f"Error deleting inspection {id}: {str(e)}")
        messages.warning(request, f"حدث خطأ اثناء حذف المعاينة: {str(e)}")
    
    return redirect("view_inspections")


@login_required(login_url="login")
def register_list_create(request):
    """
    Displays a list of all EstablishmentRegister records and provides a form
    for adding a new record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the register list template with context.
    """
    if request.method == "POST":
        form = EstablishmentRegisterForm(request.POST)
        if form.is_valid():
            register = form.save()
            logger.info(f"New establishment register created: ID {register.id} by user {request.user.username}")
            messages.success(request, "تم إضافة السجل بنجاح")
            return redirect("register-list")
    else:
        form = EstablishmentRegisterForm()

    registers = EstablishmentRegister.objects.all()
    paginator = Paginator(registers, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "today": date.today(),
        "form": form,
    }
    return render(request, "licesnsing/register_list_create.html", context)


@login_required(login_url="login")
def register_delete(request, pk):
    """
    Deletes a specific EstablishmentRegister record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the register to delete.
        
    Returns:
        HttpResponse: Redirects to the register list view.
    """
    try:
        register = get_object_or_404(EstablishmentRegister, pk=pk)
        register.delete()
        logger.info(f"Establishment register deleted: ID {pk} by user {request.user.username}")
        messages.success(request, "تم حذف السجل بنجاح")
    except Exception as e:
        logger.error(f"Error deleting register {pk}: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء حذف السجل: {str(e)}")
    
    return redirect("register-list")


@login_required(login_url="login")
def licence_list_create(request):
    """
    Displays a list of all EstablishmentLicence records and provides a form
    for adding a new record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the licence list template with context.
    """
    if request.method == "POST":
        form = EstablishmentLicenceForm(request.POST)
        if form.is_valid():
            licence = form.save()
            logger.info(f"New establishment licence created: ID {licence.id} by user {request.user.username}")
            messages.success(request, "تم إضافة الرخصة بنجاح")
            return redirect("licence-list")
    else:
        form = EstablishmentLicenceForm()

    licences = EstablishmentLicence.objects.all()
    paginator = Paginator(licences, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "form": form,
    }
    return render(request, "licesnsing/licence_list_create.html", context)


@login_required(login_url="login")
def licence_delete(request, pk):
    """
    Deletes a specific EstablishmentLicence record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the licence to delete.
        
    Returns:
        HttpResponse: Redirects to the licence list view.
    """
    licence = get_object_or_404(EstablishmentLicence, pk=pk)
    
    if request.method == "POST":
        licence.delete()
        logger.info(f"Establishment licence deleted: ID {pk} by user {request.user.username}")
        messages.success(request, "تم حذف الرخصة بنجاح")
    
    return redirect("licence-list")


@login_required(login_url="login")
def view_inspection_assignments(request):
    """
    Displays all inspection assignments.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the assignments template with context.
    """
    assignments = InspectionAssignment.objects.all()
    return render(
        request, "licesnsing/inspectors_assignments.html", {"assignments": assignments}
    )


@login_required(login_url="login")
def edit_assignment(request, pk):
    """
    Placeholder for editing an InspectionAssignment.
    
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the assignment.
        
    Returns:
        HttpResponse: Renders the edit assignment template.
    """
    # TODO: Implement assignment editing functionality
    logger.debug(f"Assignment edit view accessed for ID {pk} (not yet implemented)")
    return render(request, "licesnsing/edit_assignment.html", {})


@login_required(login_url="login")
def delete_assignment(request, pk):
    """
    Deletes an InspectionAssignment.
    
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the assignment to delete.
        
    Returns:
        HttpResponse: Redirects to the assignments list view.
    """
    try:
        assignment = get_object_or_404(InspectionAssignment, pk=pk)
        assignment.delete()
        logger.info(f"Inspection assignment deleted: ID {pk} by user {request.user.username}")
        messages.success(request, "تم حذف التكليف بنجاح")
    except Exception as e:
        logger.error(f"Error deleting assignment {pk}: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء حذف التكليف: {str(e)}")

    return redirect("view_assignments")


@login_required
@require_POST
def update_assignment_status(request, pk):
    """
    Updates the status of an InspectionAssignment.
    
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the assignment.
        
    Returns:
        HttpResponse: Redirects to the assignments list view.
    """
    new_status = request.POST.get("status")
    assignment = get_object_or_404(InspectionAssignment, id=pk)

    valid_statuses = ["pending", "accepted", "in_progress", "completed", "cancelled"]
    if new_status not in valid_statuses:
        logger.warning(f"Invalid status '{new_status}' attempted for assignment {pk} by user {request.user.username}")
        messages.error(request, "الحالة التي قمت بإدخالها خطأ.")
    else:
        assignment.status = new_status
        assignment.save()
        logger.info(f"Assignment {pk} status updated to '{new_status}' by user {request.user.username}")
        messages.success(request, "تم تحديث حالة التكليف بنجاح.")
    
    return redirect("view_assignments")


@login_required
def assign_establishment(request):
    """
    Handles assigning an establishment for inspection.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the assignment form or redirects after submission.
    """
    if request.method == "POST":
        form = InspectionAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            logger.info(f"New inspection assignment created: ID {assignment.id} by user {request.user.username}")
            messages.success(request, "تم توجيه التكليف بنجاح")
            return redirect("view_assignments")
        else:
            logger.warning(f"Assignment form validation failed: {form.errors}")
            messages.warning(request, form.errors.as_text())
    
    # Get inspectors with appropriate permissions
    inspectors = Profiles.objects.filter(occupation__power=6)
    
    # Get establishments that aren't currently assigned for inspection
    unassigned_establishments = Establishment.objects.exclude(
        inspection_assignments__isnull=False,
        inspection_assignments__status='pending'
    )
    
    if not unassigned_establishments:
        logger.info("No unassigned establishments available for inspection")
        messages.warning(request, "جميع المنشآت قد تم تعيينها.")
    
    form = InspectionAssignmentForm()
    return render(
        request,
        "licesnsing/assign_establishment.html",
        {
            "form": form,
            "unassigned_establishments": unassigned_establishments,
            "inspectors": inspectors,
        },
    )


@login_required(login_url="login")
def create_inspection(request):
    """
    Creates a new Inspection record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the inspection form or redirects after submission.
    """
    if request.method == "POST":
        form = InspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save()
            logger.info(f"New inspection created: ID {inspection.id} by user {request.user.username}")
            messages.success(request, "تم إنشاء المعاينة بنجاح!")
            return redirect("reader")
        else:
            logger.warning(f"Inspection form validation failed: {form.errors}")
            messages.error(request, "الرجاء تصحيح الأخطاء أدناه.")
            return render(
                request,
                "licesnsing/create_inspection.html",
                {"form": form}
            )
    
    form = InspectionForm()
    registers = EstablishmentRegister.objects.all()
    return render(
        request,
        "licesnsing/create_inspection.html",
        {"form": form, "registers": registers},
    )


@login_required(login_url="login")
def view_inspections(request):
    """
    Displays a paginated list of all non-archived Inspection records.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the inspections list template with context.
    """
    inspections = Inspection.objects.filter(is_archived=False).order_by('-created_at')
    paginator = Paginator(inspections, 5)
    page_obj = paginator.get_page(request.GET.get("page"))
    logger.info(f"User {request.user.username} viewed inspections list (page: {request.GET.get('page', 1)})")
    return render(request, "licesnsing/view_inspections.html", {"page_obj": page_obj})


@login_required(login_url="login")
def view_inspection_data(request, pk):
    """
    Displays detailed data for a specific inspection.
    
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the inspection.
        
    Returns:
        HttpResponse: Renders the inspection detail template.
    """
    inspection = get_object_or_404(Inspection, id=pk)
    logger.info(f"User {request.user.username} viewed inspection details for ID {pk}")
    return render(
        request, "licesnsing/view_inspection_data.html", {"inspection": inspection}
    )


@login_required(login_url="login")
def archive_inspection(request, pk):
    """
    Archives an inspection.
    
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the inspection to archive.
        
    Returns:
        HttpResponse: Redirects to the inspections list view.
    """
    inspection = get_object_or_404(Inspection, pk=pk)
    inspection.is_archived = True
    inspection.archived_at = datetime.now()
    inspection.save()
    logger.info(f"Inspection archived: ID {pk} by user {request.user.username}")
    messages.success(request, "تم أرشفة المعاينة بنجاح!")
    return redirect("view_inspections")


@login_required(login_url="login")
def view_archive(request):
    """
    Displays a list of all archived Inspection records.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the archived inspections template.
    """
    inspections = Inspection.objects.filter(is_archived=True)
    logger.info(f"User {request.user.username} viewed archived inspections")
    return render(
        request, "licesnsing/view_archived.html", {"inspections": inspections}
    )


@login_required
def add_establishment_register(request):
    """
    Adds a new EstablishmentRegister record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the register form or redirects after submission.
    """
    establishments = Establishment.objects.all()
    if request.method == "POST":
        form = EstablishmentRegisterForm(request.POST)
        if form.is_valid():
            establishment = form.cleaned_data["establishment"]

            # Check if this establishment already has a register
            if EstablishmentRegister.objects.filter(
                establishment=establishment
            ).exists():
                logger.warning(f"Attempt to create duplicate register for establishment ID {establishment.id}")
                messages.error(request, "هذا السجل موجود بالفعل لهذه المؤسسة!")
            else:
                register = form.save()
                logger.info(f"New establishment register created: ID {register.id} for establishment {establishment.establishment_name}")
                messages.success(request, "تمت إضافة السجل بنجاح!")
                return redirect("register-list")
        else:
            logger.warning(f"Register form validation failed: {form.errors}")
            messages.error(request, "الرجاء تصحيح الأخطاء في النموذج.")
    else:
        form = EstablishmentRegisterForm()

    
    return render(
        request,
        "licesnsing/establishment_register_form.html",
        {"form": form, "establishments": establishments},
    )


@login_required
def add_establishment_licence(request):
    """
    Adds a new EstablishmentLicence record.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the licence form or redirects after submission.
    """
    if request.method == "POST":
        form = EstablishmentLicenceForm(request.POST)
        if form.is_valid():
            register = form.cleaned_data["register"]

            # Check if this register already has a license
            if EstablishmentLicence.objects.filter(register=register).exists():
                logger.warning(f"Attempt to create duplicate licence for register ID {register.id}")
                messages.error(request, "يوجد بالفعل رخصة لهذا التسجيل!")
            else:
                licence = form.save()
                logger.info(f"New establishment licence created: ID {licence.number} for register {register.id}")
                messages.success(request, "تمت إضافة الرخصة بنجاح!")
                return redirect("licence-list")
        else:
            logger.warning(f"Licence form validation failed: {form.errors}")
            messages.error(request, "الرجاء تصحيح الأخطاء في النموذج.")

    else:
        form = EstablishmentLicenceForm()

    return render(request, "licesnsing/establishment_licence_form.html", {"form": form})


@login_required(login_url="login")
def get_inspector_assignments(request):
    """
    Displays all inspection assignments for the currently logged-in inspector.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the inspector assignments template.
    """
    inspector = request.user
    assignments = InspectionAssignment.objects.filter(inspector=inspector)
    logger.info(f"Inspector {inspector.username} viewed their assignments")
    return render(
        request, "licesnsing/inspector_assignments.html", {"assignments": assignments}
    )


@login_required(login_url="login")
def get_inspector_inspections(request):
    """
    Displays all inspections for the currently logged-in inspector.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the inspector inspections template.
    """
    inspector = request.user
    inspections = Inspection.objects.filter(inspector=inspector)
    return render(
        request, "licesnsing/inspector_inspections.html", {"inspections": inspections}
    )


def not_found404(request, exception):
    """
    Handles 404 Not Found errors.
    
    Args:
        request (HttpRequest): The HTTP request object.
        exception: The exception that was raised.
        
    Returns:
        HttpResponse: Renders the 404 error template.
    """
    return render(request, "errors/404.html", status=404)


def internal_server_error(request):
    """
    Handles 500 Internal Server Error errors.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: Renders the 500 error template.
    """
    return render(request, "errors/500.html", status=500)
