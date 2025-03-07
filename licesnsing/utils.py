import logging
from hashlib import md5
import os
import datetime
from django.contrib.auth.models import User

from licesnsing.models import Inspection, InspectionAssignment, Establishment, EstablishmentRegister


def send_mail(subject, body, sender, recipients):
    """Send email to recipients."""
    print(f"Sending email to {recipients} with subject: {subject} and body: {body}")


def generate_random_name():
    """Generating a random name using time and md5 hash function"""
    return md5(str(datetime.datetime.now().microsecond * 1000).encode()).hexdigest()


def upload_file(file_object, folder) -> str:
    """Saving photo object to specific folder"""
    while True:
        image_name_in_db = (
            generate_random_name() + "." + file_object.name.split(".")[-1]
        )
        image_path = os.path.join(
            folder,
            image_name_in_db,
        )
        if not os.path.exists(image_path):
            file_object.write(file_object)
            file_object.close()
            return image_name_in_db


def save_photo(photo_obj) -> str:
    """Saving photo object to specific folder"""
    return upload_file(photo_obj, "UPLOAD_FOLDER")


# Helper function to save photos
def save_photos(files):
    """Save and return paths for photos."""
    photos = {}
    for key, file in files.items():
        # Assuming you have a save_photo function
        photos[key] = save_photo(file)
    return photos


# Helper function to send email
def send_inspection_email(status, email, notes=None):
    """Send inspection status emails."""
    subject = "Inspection Accepted" if status else "Inspection Refused"
    body = f"Inspection {'Accepted' if status else 'Refused'}" + (
        f": \n{notes}" if notes else ""
    )
    try:
        send_mail(subject, body, "from@example.com", [email])
    except Exception as e:
        print(f"Error sending email: {e}")


def mark_inspection_as_done(establishment):
    """Mark inspection as done in the database."""
    try:
        inspection = InspectionAssignment.objects.get(establishment_id=establishment.id)
        inspection.status = "completed"
        inspection.save()
    except Exception as e:
        print(f"Error marking inspection as done: {e}")

def get_establishment_obj_by_register(register_id):
    """Get establishment object by register id."""
    try:
        establishment = EstablishmentRegister.objects.get(id=register_id).establishment
        return establishment
    except Exception as e:
        print(f"Error getting establishment by register id: {e}")
        return None

# Helper function to handle inspection logic
def process_inspection(form_data, photos):
    """Process the inspection and save to DB."""
    # inspector = User.objects.get(id=current_user.id)
    inspect = dict(
        register_number=form_data["register_number"],
        notes=form_data["notes"],
        latitude=form_data["latitude"],
        longitude=form_data["longitude"],
        status=form_data["status"],
        register_photo=photos["register_photo"],
        license_photo=photos["license_photo"],
        establishment_photo=photos["establishment_photo"],
        cars_building_photo=photos["cars_building_photo"],
    )
    return inspect


# Main view


# Helper function to process the raw request body (Arduino request)
def process_raw_data(request):
    """Process the raw data from the Arduino request."""
    try:
        # The Arduino sends raw data in the format: 'key=value'
        data = request.body.decode()
        code = data.split("=")[1]  # Extract the code
        return code
    except Exception as e:
        logging.error(f"Error processing raw data: {e}")
        return None


# Helper function to process form data
def process_form_data(request):
    """Process form data from the Arduino request."""
    try:
        code = request.POST.get("UIDresult")
        return code
    except Exception as e:
        logging.error(f"Error processing form data: {e}")
        return None
