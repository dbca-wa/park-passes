"""
    This module contains the models required to impliment passes.

    - PassType (Local, Holiday, Annual etc.)
    - PassTypePricingWindow (A period of time that specific pricing can be specified)
    - PassTypePricingWindowOption (The duration options for a pass i.e. 5 days, 14 days, etc.)
    - Pass (The pass itself which contains the information required to generate the QR Code)
"""
import qrcode
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import models
from ledger_api_client.ledger_models import EmailUserRO as EmailUser


class PassType(models.Model):
    """A class to represent a pass type"""

    image = models.ImageField()
    name = models.CharField(editable=False)  # Name reserved for system use
    display_name = models.CharField()
    display_order = models.SmallIntegerField()
    display_externally = models.BooleanField()


class PassTypePricingWindow(models.Model):
    """A class to represent a pass type pricing window"""

    pass_type = models.ForeignKey(PassType, on_delete=models.PROTECT)
    active_from = models.DateTimeField()
    expiry = models.DateTimeField()


class PassTypePricingWindowOption(models.Model):
    """A class to represent a pass type pricing window option"""

    pricing_window = models.ForeignKey(PassTypePricingWindow, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)  # i.e. '5 days'
    duration = models.SmallIntegerField()  # in days i.e. 5, 14, 28, 365
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)


def park_pass_pdf_path(instance, filename):
    """Stores the park pass pdf in a unique folder based on the pass pk"""
    return f"passes/{instance.pk}/{filename}"


class Pass(models.Model):
    """A class to represent a pass"""

    user = models.ForeignKey(EmailUser, on_delete=models.PROTECT, blank=True, null=True)
    option = models.ForeignKey(PassTypePricingWindowOption, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    vehicle_registration_1 = models.CharField(max_length=10, null=True, blank=True)
    vehicle_registration_2 = models.CharField(max_length=10, null=True, blank=True)
    postcode = models.CharField(max_length=4, null=True, blank=True)
    active_from = models.DateTimeField()
    expiry = models.DateTimeField(null=False, blank=False)
    encrypted_link_hash = models.CharField(max_length=150, null=True, blank=True)
    renew_automatically = models.BooleanField(null=False)
    park_pass_pdf = models.FileField(
        upload_to=park_pass_pdf_path, null=True, blank=True
    )

    def generate_qrcode(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        pass_data_json = serializers.serialize("json", self)
        # replace this line with the real encryption server at a later date
        encrypted_pass_data = self.imaginary_encryption_endpoint(pass_data_json)
        qr.add_data(encrypted_pass_data)
        qr.make(fit=True)
        qr_image = qrcode.make_image(fill="black", back_color="white")
        qr_image.save(park_pass_pdf_path(self, "qrcode.png"))

    def imaginary_encryption_endpoint(self, json_pass_data):
        return json_pass_data + json_pass_data


class HolidayPass(Pass):
    """A proxy class to represent a holiday pass"""

    class Meta:
        proxy = True

    def save(self):
        pass


class LocalParkPass(Pass):
    """A proxy class to represent a local park pass"""

    class Meta:
        proxy = True

    def save(self):
        pass


class GoldStarPass(Pass):
    """A proxy class to represent a gold star pass"""

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        # if the user does not have a postal address
        # raise a ValidationError exception
        if False:
            raise ValidationError
        super().save(*args, **kwargs)


class DayEntryPass(Pass):
    """A proxy class to represent a day entry pass"""

    class Meta:
        proxy = True

    def save(self):
        pass
