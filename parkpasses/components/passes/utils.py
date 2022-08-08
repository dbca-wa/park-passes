"""
    This module provides utilities for the passes component
"""

import logging
import os
import subprocess
from pathlib import Path

from django.conf import settings
from django.utils.dateformat import DateFormat
from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage

logger = logging.getLogger(__name__)


class PassUtils:
    def generate_pass_pdf_from_docx_template(
        self, park_pass, pass_template, qr_code_path
    ):

        park_pass_docx = DocxTemplate(
            f"{settings.PROTECTED_MEDIA_ROOT}/{pass_template.template.name}"
        )

        qr_image = InlineImage(
            park_pass_docx, image_descriptor=qr_code_path, width=Mm(60)
        )

        date_format = DateFormat(park_pass.datetime_start)
        datetime_start = date_format.format("jS F Y")

        date_format = DateFormat(park_pass.datetime_expiry)
        datetime_expiry = date_format.format("jS F Y")

        date_format = DateFormat(park_pass.datetime_created)
        datetime_created = date_format.format("jS F Y")

        context = {
            "pass_qr_code": qr_image,
            "pass_type": park_pass.option.pricing_window.pass_type.display_name,
            "pass_start": datetime_start,
            "pass_expiry": datetime_expiry,
            "pass_vehicle_registration_1": park_pass.vehicle_registration_1,
            "pass_vehicle_registration_2": park_pass.vehicle_registration_2,
            "pass_purchase_date": datetime_created,
        }

        park_pass_docx.render(context)
        park_pass_file_path = f"{park_pass._meta.app_label}/"
        park_pass_file_path += (
            f"{park_pass._meta.model.__name__}/passes/{park_pass.user}/{park_pass.pk}/"
        )
        Path(park_pass_file_path).mkdir(parents=True, exist_ok=True)

        park_pass_docx_file_name = "ParkPass.docx"
        park_pass_docx_full_file_path = (
            settings.PROTECTED_MEDIA_ROOT
            + "/"
            + park_pass_file_path
            + park_pass_docx_file_name
        )
        park_pass_docx.save(f"{park_pass_docx_full_file_path}")
        output = subprocess.check_output(
            [
                "libreoffice",
                "--convert-to",
                "pdf",
                park_pass_docx_full_file_path,
                "--outdir",
                settings.PROTECTED_MEDIA_ROOT + "/" + park_pass_file_path,
            ]
        )

        logger.debug("output = " + str(output))

        # convert(f"{park_pass_file_path}/{park_pass_docx_file_name}")

        park_pass_pdf_file_name = "ParkPass.pdf"
        park_pass_pdf_path = park_pass_file_path + park_pass_pdf_file_name
        park_pass.park_pass_pdf.name = park_pass_pdf_path
        park_pass.save(update_fields=["park_pass_pdf"])
        # Clean up unused files
        os.remove(park_pass_docx_full_file_path)
        os.remove(qr_code_path)
