from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from .forms import (
    CustomUserCreationForm,
    ProfileForm,
    ContactForm,
    UserFullForm,
    TeamForm, UserEditForm,
)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

from .models import Team, Occupation


# Create your views here.
@login_required(login_url="login")
def profiles_list(request):
    """

    Display a list of all user profiles along with their related information.


    This view retrieves all Profiles records from the database, including related data
    (User, Contact, Occupation, and Team), and renders them in the 'profiles_list.html'
    template.

    Context:
        profiles (QuerySet): A queryset of all Profiles objects.
    """

    profiles = User.objects.all()
    return render(request, "users/profiles_list.html", {"profiles": profiles})




@login_required(login_url="login")
def edit_user_profile(request, pk):
    """
    Edit an existing User and Profile.
    """
    user = User.objects.get(pk=pk)
    profile = user.profiles
    contact = profile.contact
    user_form = CustomUserCreationForm(request.POST or None, instance=user)
    profile_form = ProfileForm(
        request.POST or None, request.FILES or None, instance=profile
    )
    contact_form = ContactForm(request.POST or None, instance=contact)
    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid() and contact_form.is_valid():
            user_form.save()
            profile_form.save()
            contact_form.save()
            messages.success(request, "User and profile updated successfully!")
            return redirect("profiles-list")  # Change to your desired redirect URL
        else:
            messages.error(
                request,
                "There were errors in the form. Please correct them and try again.",
            )
            return render(
                request,
                "users/edit_user_profile.html",
                {
                    "user_form": user_form,
                    "profile_form": profile_form,
                    "contact_form": contact_form,
                },
            )

    return render(
        request,
        "users/edit_user_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "contact_form": contact_form,
        },
    )


@login_required(login_url="login")
def delete_user_profile(request, pk):
    """
    Delete an existing User and Profile.
    """
    user = User.objects.get(pk=pk)
    profile = user.profiles
    contact = profile.contact
    user.delete()
    contact.delete()
    profile.delete()
    messages.success(request, "User and profile deleted successfully!")
    return redirect("profiles-list")  # Change to your desired redirect URL


def login_view(request):
    """
    Handles user login.

    GET: Displays the login form.
    POST: Validates the submitted form and logs in the user if credentials are correct.
    """
    # get next page args
    next_url = request.GET.get("next")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"مرحباً, {user.username}!")
            if not next_url:
                next_url = "dashboard"
            return redirect(
                next_url
            )  # Replace 'dashboard' with your desired redirect URL name.
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm(request)

    return render(request, "users/login.html", {"form": form})


@login_required(login_url="login")
def create_new_user(request):
    """
    View to create a new Django User using UserFullForm.

    GET: Displays an empty form for creating a new user.
    POST: Validates and saves the form data. If successful, redirects
          to a user list view. Otherwise, the form with error messages is re-rendered.
    """
    if request.method == "POST":
        form = UserFullForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if form.is_valid() and profile_form.is_valid():

            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "تم انشاء المستخدم بنجاح!")

        else:
            messages.error(request, "Please correct the errors below.")
        return redirect(
            "profiles-list"
        )  # Replace with your desired redirect URL name.
    else:
        form = UserFullForm()
        profile_form = ProfileForm(request.POST, request.FILES)
        occupations = Occupation.objects.all()
        teams = Team.objects.all()
        return render(
            request, "users/register.html", {"form": form, "profile_form": profile_form, "occupations": occupations, "teams": teams}
        )


def logout_view(request):
    """

    :param request:
    :return:
    """
    logout(request)
    return render(request, "users/login.html")


@login_required(login_url="login")
def view_teams(request):
    """
    View to display all teams in the database.
    """
    teams = Team.objects.all()
    return render(request, "users/view_teams.html", {"teams": teams})


def team_edit(request, id):
    team = get_object_or_404(Team, id=id)
    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الفريق بنجاح!")
            return redirect("teams")
    else:
        form = TeamForm(instance=team)
    return redirect("teams")


def team_delete(request, id):
    team = get_object_or_404(Team, id=id)
    if request.method == "POST":
        team.delete()
        messages.success(request, "تم حذف الفريق بنجاح!")
        return redirect("teams")  # Redirect to a list of teams after deletion
    return redirect("teams")


def team_create(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            # Save the new team to the database
            form.save()
            messages.success(request, "تم انشاء الفريق بنجاح!")
            # You can return a success response or redirect
            return redirect(
                "teams"
            )  # Redirect to the teams list page or another view after saving
        else:
            # Return errors if the form is invalid
            messages.error(request, "الرجاء التاكد من اسم الفريق!")
            return redirect("teams")
    else:
        # GET request (for showing the empty form)
        form = TeamForm()
        return redirect("teams")


def user_edit(request, id):
    """
    Edit a user account.
    :param request:
    :param id:
    :return:
    """

    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # ✅ Save user details WITHOUT changing the password
            return redirect("profiles-list")  # Redirect after successful update
    else:
        form = UserEditForm(instance=user)

    return render(request, "users/edit_user.html", {"form": form, "user": user})


def user_deactivate(request, id):
    """
    Deactivate a user account.

    :param request:
    :param id:
    :return:
    """
    user = get_object_or_404(User, id=id)
    if user:
        user.is_active = False
        user.save()
        messages.success(request, "تم تعطيل المستخدم بنجاح!")
    else:
        messages.error(request, "حدث خطأ اثناء تعطيل المستخدم!")
    return redirect("profiles-list")


def user_activate(request, id):
    """
    Activate a user account.
    :param request:
    :param id:
    :return:
    """
    user = get_object_or_404(User, id=id)
    if user:
        user.is_active = True
        user.save()
        messages.success(request, "تم تفعيل المستخدم بنجاح!")
        return redirect("profiles-list")
    else:
        messages.error(request, "حدث خطأ اثناء تفعيل المستخدم!")
    return redirect("profiles-list")


def user_delete(request, id):
    """
    Delete a user account.
    :param request:
    :param id:
    :return:
    """
    user = get_object_or_404(User, id=id)
    if user:
        user.delete()
        messages.success(request, "تم حذف المستخدم بنجاح!")
        return redirect("profiles-list")
    else:
        messages.error(request, "حدث خطأ اثناء حذف المستخدم!")
    return redirect("profiles-list")
