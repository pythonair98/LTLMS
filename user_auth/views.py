from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, ContactForm


# Create your views here.
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


def create_user_profile(request):
    """
    Create a new User along with an associated Profile and Contact in one form.

    On GET: Display empty forms for the User, Profile, and Contact.
    On POST: Validate all forms and, if valid, create a new User,
             create a Contact, and then create a Profile linking them.
    """
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        contact_form = ContactForm(request.POST)

        # Use an atomic transaction to ensure all-or-nothing saving
        if user_form.is_valid() and profile_form.is_valid() and contact_form.is_valid():
            with transaction.atomic():
                # Save the user first
                user = user_form.save()
                # Save the contact information
                contact = contact_form.save()
                # Create the profile instance but do not commit to the DB yet
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.contact = contact
                profile.save()
            messages.success(request, "User and profile created successfully!")
            return redirect("profiles-list")  # Change to your desired redirect URL
        else:
            messages.error(
                request,
                "There were errors in the form. Please correct them and try again.",
            )
    else:
        user_form = CustomUserCreationForm()
        profile_form = ProfileForm()
        contact_form = ContactForm()

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "contact_form": contact_form,
    }
    return render(request, "users/create_user_profile.html", context)


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
