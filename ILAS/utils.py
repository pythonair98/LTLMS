import logging
from hashlib import md5
import os
import datetime

from .models import (
    InspectionAssignment,
    EstablishmentRegister,
)

def send_mail(subject, body, sender, recipients):
    """
    Sends an email to the specified recipients.

    Parameters:
        subject (str): The subject of the email.
        body (str): The body content of the email.
        sender (str): The sender's email address.
        recipients (list): A list of recipient email addresses.

    Returns:
        None
    """
    print(f"Sending email to {recipients} with subject: {subject} and body: {body}")

def generate_random_name():
    """
    Generates a random file name using the current timestamp and md5 hash.

    Returns:
        str: A unique hashed string.
    """
    return md5(str(datetime.datetime.now().microsecond * 1000).encode()).hexdigest()

def upload_file(file_object, folder) -> str:
    """
    Saves a file to the specified folder with a unique name.

    Parameters:
        file_object (File): The file object to be saved.
        folder (str): The target folder where the file will be stored.

    Returns:
        str: The generated filename saved in the database.
    """
    while True:
        image_name_in_db = (
            generate_random_name() + "." + file_object.name.split(".")[-1]
        )
        image_path = os.path.join(folder, image_name_in_db)
        if not os.path.exists(image_path):
            file_object.write(file_object)
            file_object.close()
            return image_name_in_db

def save_photo(photo_obj) -> str:
    """
    Saves a photo object to a predefined upload folder.

    Parameters:
        photo_obj (File): The photo object to be stored.

    Returns:
        str: The filename of the saved photo.
    """
    return upload_file(photo_obj, "UPLOAD_FOLDER")

def save_photos(files):
    """
    Saves multiple photo files and returns their paths.

    Parameters:
        files (dict): A dictionary of file objects.

    Returns:
        dict: A dictionary with filenames for each saved file.
    """
    photos = {}
    for key, file in files.items():
        photos[key] = save_photo(file)
    return photos

def send_inspection_email(status, email, notes=None):
    """
    Sends an email notification based on the inspection status.

    Parameters:
        status (bool): Inspection status (True for accepted, False for refused).
        email (str): Recipient's email address.
        notes (str, optional): Additional notes for the email body.

    Returns:
        None
    """
    subject = "Inspection Accepted" if status else "Inspection Refused"
    body = f"Inspection {'Accepted' if status else 'Refused'}" + (f": \n{notes}" if notes else "")
    try:
        send_mail(subject, body, "from@example.com", [email])
    except Exception as e:
        print(f"Error sending email: {e}")

def mark_inspection_as_done(establishment):
    """
    Marks an inspection as completed in the database.

    Parameters:
        establishment (Establishment): The establishment object linked to the inspection.

    Returns:
        None
    """
    try:
        inspection = InspectionAssignment.objects.get(establishment_id=establishment.id)
        inspection.status = "completed"
        inspection.save()
    except Exception as e:
        print(f"Error marking inspection as done: {e}")

def get_establishment_obj_by_register(register_id):
    """
    Retrieves an establishment object using its register ID.

    Parameters:
        register_id (int): The register ID associated with the establishment.

    Returns:
        Establishment: The establishment object if found.
        None: If an error occurs.
    """
    try:
        establishment = EstablishmentRegister.objects.get(id=register_id).establishment
        return establishment
    except Exception as e:
        print(f"Error getting establishment by register id: {e}")
        return None

def process_inspection(form_data, photos):
    """
    Processes the inspection data and formats it for saving to the database.

    Parameters:
        form_data (dict): A dictionary containing inspection details.
        photos (dict): A dictionary containing paths to uploaded photos.

    Returns:
        dict: A dictionary containing structured inspection data.
    """
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

def process_raw_data(request):
    """
    Processes raw data received from an Arduino request.

    Parameters:
        request (HttpRequest): The HTTP request containing raw data.

    Returns:
        str: Extracted data from the request body.
        None: If an error occurs.
    """
    try:
        data = request.body.decode()
        code = data.split("=")[1]
        return code
    except Exception as e:
        logging.error(f"Error processing raw data: {e}")
        return None

def process_form_data(request):
    """
    Processes form data received from an Arduino request.

    Parameters:
        request (HttpRequest): The HTTP request object containing form data.

    Returns:
        str: The value of the 'UIDresult' field from the form data if present.
        None: If an exception occurs.
    """
    try:
        code = request.POST.get("UIDresult")
        return code
    except Exception as e:
        logging.error(f"Error processing form data: {e}")
        return None

def inspector_assignments(user):
    """
    Retrieves the count of pending inspection assignments for a given inspector.

    Parameters:
        user (User): The inspector whose assignments are to be retrieved.

    Returns:
        int: Number of pending assignments.
        None: If an error occurs.
    """
    try:
        assignments = InspectionAssignment.objects.filter(
            inspector=user, status="pending"
        ).count()
        return assignments if assignments else 0
    except Exception as e:
        logging.error(f"Error retrieving assignments: {e}")
        return None
