from .models import (
    InspectionAssignment,
    EstablishmentRegister,
)
import subprocess
import os
import uuid

from django.conf import settings
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR



def mark_inspection_as_done(establishment):
    """
    Marks an inspection as completed in the database.

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
    """
    try:
        establishment = EstablishmentRegister.objects.get(id=register_id).establishment
        return establishment
    except Exception as e:
        print(f"Error getting establishment by register id: {e}")
        return None



from ILAS.models import EstablishmentLicence, Establishment


class PowerPointUpdater:
    def __init__(self, presentation_path, cell_values):
        """
        Initialize the PowerPointUpdater with the path to the presentation and the dictionary of cell values.
        """
        self.prs = Presentation(presentation_path)
        self.cell_values = cell_values

    def update_table_cells(self):
        """
        Update the text in table cells based on the cell_values dictionary.
        """
        for slide_idx, slide in enumerate(self.prs.slides):

            for shape_idx, shape in enumerate(slide.shapes):
                if shape.has_table:

                    for row in shape.table.rows:
                        for cell in row.cells:
                            # Check if the cell text matches any key in the dictionary
                            if cell.text in self.cell_values:
                                cell.text = self.cell_values[cell.text]

                                self._center_align_text(cell)
                elif hasattr(shape, "text"):
                    # Update text for non-table shapes if their text matches any key in the dictionary
                    if shape.text in self.cell_values:
                        shape.text = self.cell_values[shape.text]

    def _center_align_text(self, cell):
        """
        Center-align text both vertically and horizontally in a table cell.
        """
        cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        for paragraph in cell.text_frame.paragraphs:
            paragraph.alignment = PP_ALIGN.CENTER

    def save_presentation(self, output_path):
        """
        Save the updated presentation to the specified output path.
        """
        self.prs.save(output_path)


class PPTtoPDFConverter:
    @staticmethod
    def convert(input_file):
        """
        Convert a PowerPoint presentation to a PDF using LibreOffice.
        """
        # Full path to the LibreOffice executable
        libreoffice_path = "/usr/bin/libreoffice"  # Adjust this path if LibreOffice is installed elsewhere

        # Generate a random file name for the PDF

        output_file = os.path.join(settings.BASE_DIR,"static/files/reports_temp", input_file)
        print("OutFile:", output_file)
        command = [
            libreoffice_path,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            os.path.dirname(output_file),
            input_file,
        ]
        print(command)
        subprocess.run(command, check=True)

        # Return the absolute path of the generated PDF file
        return os.path.abspath(output_file)


def create_license_report(licence_:EstablishmentLicence, establishment:Establishment, register):
    presentation_path = os.path.join(settings.BASE_DIR,"static/files/reports_temp", "license_report.pptx")
    updated_presentation_path = str(uuid.uuid4()) + ".pptx"

    cell_values = {
        "Owner_name": establishment.owner_name,
        "Register_number": register.id,
        "Establishment_name": establishment.establishment_name,
        "Id_number": establishment.owner_number,
        "License_category": licence_.main_category_id,
        "Issue_date": licence_.creation_date,
        "Expired_date": licence_.expiration_date,
        "Activity": licence_.activity.ar_name,
        "Address": establishment.get_address(),
        "License_number": licence_.number,
        "Phone_number": establishment.phone_number,
        "Email": establishment.email,
    }

    # Create an instance of PowerPointUpdater, update the table cells, and save the updated presentation
    updater = PowerPointUpdater(presentation_path, cell_values)
    updater.update_table_cells()
    updater.save_presentation(updated_presentation_path)

    # Convert the updated presentation to a PDF and get the absolute path of the generated PDF file
    pdf_path = PPTtoPDFConverter.convert(os.path.abspath(updated_presentation_path))
    return pdf_path


