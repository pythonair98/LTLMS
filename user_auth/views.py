from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from typing import Optional, Tuple
import logging

from ILAS.utils import inspector_assignments
from .forms import (
    CustomUserCreationForm,
    ProfileForm,
    ContactForm,
    UserFullForm,
    TeamForm,
    UserEditForm,
)
from .models import Team, Occupation, Profiles
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Create your views here.
@login_required(login_url="login")
def profiles_list(request):
    """Display a list of all user profiles.

    Retrieves all User records from the database and renders them in the 
    'profiles_list.html' template.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with all user profiles
    """
    profiles = User.objects.all()
    return render(request, "users/profiles_list.html", {"profiles": profiles})


@login_required(login_url="login") 
def edit_user_profile(request, pk):
    """Edit an existing User and Profile.

    Args:
        request: The HTTP request object
        pk: Primary key of the user to edit

    Returns:
        Rendered edit form or redirect after successful update
    """
    user = get_object_or_404(User, pk=pk)
    profile = user.profiles
    contact = profile.contact

    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        contact_form = ContactForm(request.POST, instance=contact)

        if all([user_form.is_valid(), profile_form.is_valid(), contact_form.is_valid()]):
            user_form.save()
            profile_form.save() 
            contact_form.save()
            messages.success(request, "User and profile updated successfully!")
            return redirect("profiles-list")

        messages.error(request, "Please correct the form errors and try again.")
        
    else:
        user_form = CustomUserCreationForm(instance=user)
        profile_form = ProfileForm(instance=profile)
        contact_form = ContactForm(instance=contact)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "contact_form": contact_form,
    }
    return render(request, "users/edit_user_profile.html", context)


@login_required(login_url="login")
def delete_user_profile(request, pk):
    """Delete an existing User and related Profile.

    Args:
        request: The HTTP request object
        pk: Primary key of user to delete

    Returns:
        Redirect to profiles list
    """
    user = get_object_or_404(User, pk=pk)
    profile = user.profiles
    contact = profile.contact
    
    user.delete()
    contact.delete()
    profile.delete()
    
    messages.success(request, "User and profile deleted successfully!")
    return redirect("profiles-list")


def login_view(request):
    """Handle user login.

    GET: Display login form
    POST: Validate credentials and log in user

    Args:
        request: The HTTP request object

    Returns:
        Rendered login form or redirect after successful login
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        
        return redirect("dashboard")

    next_url = request.GET.get("next", "dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            assignment_count = inspector_assignments(user)
            if assignment_count > 0:
                messages.info(request, f"يوجد لديك تكليفات عدد: {assignment_count}")
                
            messages.success(request, f"مرحباً, {user.username}!")
            return redirect(next_url)
            
        messages.error(request, "Invalid username or password.")
        
    else:
        form = AuthenticationForm(request)

    return render(request, "users/login.html", {"form": form})


@login_required(login_url="login")
def create_new_user(request):
    """Create a new user account.

    GET: Display registration form
    POST: Create new user if form is valid

    Args:
        request: The HTTP request object

    Returns:
        Rendered registration form or redirect after successful creation
    """
    if request.method == "POST":
        form = UserFullForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            if not user.pk:
                user.set_password(form.cleaned_data["password"])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, "تم انشاء المستخدم بنجاح!")
            return redirect("profiles-list")

        messages.warning(request, "Please correct the errors below.")
        messages.error(request, form.errors.as_data())
        return redirect("profiles-list")

    context = {
        "form": UserFullForm(),
        "profile_form": ProfileForm(),
        "occupations": Occupation.objects.all(),
        "teams": Team.objects.all(),
    }
    return render(request, "users/register.html", context)


def logout_view(request):
    """Log out the current user.

    Args:
        request: The HTTP request object

    Returns:
        Redirect to login page
    """
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def view_teams(request):
    """Display all teams.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with all teams
    """
    teams = Team.objects.all()
    return render(request, "users/view_teams.html", {"teams": teams})


@login_required(login_url="login")
def team_edit(request, id):
    """Edit an existing team.

    Args:
        request: The HTTP request object
        id: ID of team to edit

    Returns:
        Redirect to teams list
    """
    team = get_object_or_404(Team, id=id)
    
    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الفريق بنجاح!")
    
    return redirect("teams")


@login_required(login_url="login")
def team_delete(request, id):
    """Delete an existing team.

    Args:
        request: The HTTP request object
        id: ID of team to delete

    Returns:
        Redirect to teams list
    """
    team = get_object_or_404(Team, id=id)
    
    if request.method == "POST":
        team.delete()
        messages.success(request, "تم حذف الفريق بنجاح!")
    
    return redirect("teams")


@login_required(login_url="login")
def team_create(request):
    """Create a new team.

    Args:
        request: The HTTP request object

    Returns:
        Redirect to teams list
    """
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم انشاء الفريق بنجاح!")
        else:
            messages.error(request, "الرجاء التاكد من اسم الفريق!")
    
    return redirect("teams")


@login_required(login_url="login")
def user_edit(request, id):
    """Edit a user account.

    Args:
        request: The HTTP request object
        id: ID of user to edit

    Returns:
        Rendered edit form or redirect after successful update
    """
    user = get_object_or_404(User, id=id)
    
    if user.profiles is None:
        messages.error(request, "هذا المستخدم غير مستكمل البيانات.")
        return redirect("profiles-list")
        
    profile = get_object_or_404(Profiles, user=user)

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        
        if form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, "تم تحديث المستخدم بنجاح!")
            return redirect("profiles-list")

    context = {
        "form": UserEditForm(instance=user),
        "user": user,
        "occupations": Occupation.objects.all(),
        "teams": Team.objects.all(),
    }
    return render(request, "users/edit_user.html", context)


@login_required(login_url="login")
def user_deactivate(request, id):
    """Deactivate a user account.

    Args:
        request: The HTTP request object
        id: ID of user to deactivate

    Returns:
        Redirect to profiles list
    """
    user = get_object_or_404(User, id=id)
    user.is_active = False
    user.save()
    messages.success(request, "تم تعطيل المستخدم بنجاح!")
    return redirect("profiles-list")


@login_required(login_url="login")
def user_activate(request, id):
    """Activate a user account.

    Args:
        request: The HTTP request object
        id: ID of user to activate

    Returns:
        Redirect to profiles list
    """
    user = get_object_or_404(User, id=id)
    user.is_active = True
    user.save()
    messages.success(request, "تم تفعيل المستخدم بنجاح!")
    return redirect("profiles-list")


@login_required(login_url="login")
def user_delete(request, id):
    """Delete a user account.

    Args:
        request: The HTTP request object
        id: ID of user to delete

    Returns:
        Redirect to profiles list
    """
    user = get_object_or_404(User, id=id)
    user.delete()
    messages.success(request, "تم حذف المستخدم بنجاح!")
    return redirect("profiles-list")


@login_required(login_url="login")
def get_team_members(request, id):
    """
    Get all members of a specific team.
    
    Args:
        request: The HTTP request object
        id: The team ID to get members for
        
    Returns:
        Rendered template with team members
    """
    # Get team or return 404 if not found
    team = get_object_or_404(Team, id=id)
    
    # Get all profiles associated with the team and extract users
    team_members = team.profiles_set.select_related('user').all()
    users = [profile.user for profile in team_members]
    
    return render(
        request,
        "users/profiles_list.html",
        {"profiles": users}
    )


def send_confirmation_email(request, user: Optional[User] = None) -> Tuple[bool, str]:
    """
    Send a confirmation email to the user with a verification link.
    
    Args:
        request: The HTTP request object
        user: Optional User object to send email to. If None, uses request.user
        
    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: Success status
            - str: Message describing the result
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Get user from parameter or request
        target_user = user or request.user
        if not target_user:
            return False, "No user specified"
            
        # Generate confirmation token and URL
        token = default_token_generator.make_token(target_user)
        uid = urlsafe_base64_encode(force_bytes(target_user.pk))
        confirm_url = request.build_absolute_uri(
            reverse('confirm_email', kwargs={'uidb64': uid, 'token': token})
        )

        # Prepare email content
        context = {
            'user': target_user,
            'confirm_url': confirm_url
        }
        
        # Get email configuration from settings with defaults
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@milahaarabia.com')
        subject = getattr(settings, 'EMAIL_CONFIRMATION_SUBJECT', 'Confirm your email')
        template_name = getattr(settings, 'EMAIL_CONFIRMATION_TEMPLATE', 'users/confirm_email.html')
        
        # Render email content
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)

        # Create and send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[target_user.email],
            reply_to=[from_email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        logger.info(f"Confirmation email sent successfully to {target_user.email}")
        return True, "Confirmation email sent successfully"
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        return False, f"Failed to send confirmation email: {str(e)}"


def confirm_email(request, uidb64, token):
    """
    Validate email confirmation token and activate user account.
    
    Args:
        request: The HTTP request
        uidb64: Base64 encoded user ID
        token: Confirmation token
        
    Returns:
        HttpResponse: Redirects to login page with success/error message
    """
    try:
        from django.utils.http import urlsafe_base64_decode
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.")
            return redirect('login')
        else:
            messages.error(request, "رابط التفعيل غير صالح!")
            return redirect('login')
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "رابط التفعيل غير صالح!")
        return redirect('login')

