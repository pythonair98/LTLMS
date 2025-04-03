import subprocess
import os
import uuid
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR


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

        output_file = os.path.join(os.path.dirname(input_file), input_file)
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


def create_license_report(data: dict = {}):
    presentation_path = "lic.pptx"
    updated_presentation_path = str(uuid.uuid4()) + ".pptx"

    cell_values = {
        "Owner_name": "John Doe",
        "Register_number": "123456789",
        "Establishment_name": "ABC Corp",
        "Id_number": "987654321",
        "License_category": "Driver's License",
        "Issue_date": "2025-01-01",
        "Expired_date": "2030-01-01",
        "Activity": "Driving",
        "Address": "123 Main St, Anytown, USA",
        "License_number": "D1234567",
        "Phone_number": "555-123-4567",
        "Email": "example@example.com",
    }

    # Create an instance of PowerPointUpdater, update the table cells, and save the updated presentation
    updater = PowerPointUpdater(presentation_path, cell_values)
    updater.update_table_cells()
    updater.save_presentation(updated_presentation_path)

    # Convert the updated presentation to a PDF and get the absolute path of the generated PDF file
    pdf_path = PPTtoPDFConverter.convert(os.path.abspath(updated_presentation_path))
    return pdf_path
