"""
    This module provides utilities
"""

import logging
from decimal import Decimal

from borb.pdf import PDF, Document, Page
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.forms.text_field import TextField
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.text.paragraph import Paragraph

from parkpasses import settings

logger = logging.getLogger(__name__)


class PdfGenerator:
    """Used to generate a park pass pdf"""

    def generate_park_pass_pdf(self, park_pass):
        # Create empty Document
        pdf = Document()

        # Create empty Page
        page = Page()

        # Add Page to Document
        pdf.append_page(page)

        # Create PageLayout
        layout: PageLayout = SingleColumnLayout(page)

        # Let's start by adding a heading
        layout.add(Paragraph("Patient Information:", font="Helvetica-Bold"))

        # Use a table to lay out the form
        table: FixedColumnWidthTable = FixedColumnWidthTable(
            number_of_rows=1, number_of_columns=2
        )

        # Name
        table.add(
            Paragraph(
                "Name : ",
                horizontal_alignment=Alignment.RIGHT,
                font_color=HexColor("56cbf9"),
            )
        )
        table.add(
            TextField(value="Doe", font_color=HexColor("56cbf9"), font_size=Decimal(20))
        )

        # Surname
        table.add(
            Paragraph(
                "Surname : ",
                horizontal_alignment=Alignment.RIGHT,
                font_color=HexColor("56cbf9"),
            )
        )
        table.add(
            TextField(
                value="John", font_color=HexColor("56cbf9"), font_size=Decimal(20)
            )
        )

        # Adding Table to PageLayout
        layout.add(table)

        path = f"{settings.MEDIA_ROOT}/passes/{park_pass.pk}/ParkPass.pdf"

        logger.debug("path: " + path)

        # Store
        with open(path, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, pdf)

        return path
