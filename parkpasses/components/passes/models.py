"""
    This module contains the models required to impliment passes.

    - PassType (Local, Holiday, Annual etc.)
    - PassTypePricingWindow (A period of time that specific pricing can be specified)
    - PassTypePricingWindowOption (The duration options for a pass i.e. 5 days, 14 days, etc.)
    - Pass (The pass itself which contains the information required to generate the QR Code)
"""

import logging
import math
import os
from decimal import Decimal

import qrcode
import requests
from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.core.files.storage import FileSystemStorage
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
from django_resized import ResizedImageField

from parkpasses.components.orders.models import OrderItem
from parkpasses.components.parks.models import ParkGroup
from parkpasses.components.passes.emails import PassEmails
from parkpasses.components.passes.exceptions import (
    MultipleDefaultPricingWindowsExist,
    NoDefaultOptionFoundForOptionWindowExists,
    NoDefaultPricingWindowExists,
    PassTemplateDoesNotExist,
    QRCodeEncryptionFailed,
    SendNoPrimaryCardForAutoRenewalEmailFailed,
    SendPassAutoRenewFailureNotificationEmailFailed,
    SendPassAutoRenewNotificationEmailFailed,
    SendPassAutoRenewSuccessNotificationEmailFailed,
    SendPassExpiredNotificationEmailFailed,
    SendPassExpiryNotificationEmailFailed,
    SendPassFinalAutoRenewFailureNotificationEmailFailed,
    SendPassPurchasedEmailNotificationFailed,
    SendPassVehicleDetailsNotYetProvidedEmailNotificationFailed,
)
from parkpasses.components.passes.utils import PassUtils
from parkpasses.components.retailers.models import District, RetailerGroup
from parkpasses.ledger_api_utils import retrieve_email_user

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


logger = logging.getLogger(__name__)


def pass_type_image_path(instance, filename):
    """Stores the pass type images in a unique folder

    based on the content type and object_id
    """
    return f"{instance._meta.app_label}/{instance._meta.model.__name__}/{instance.name}/{filename}"


def pass_type_template_image_path(instance, filename):
    """Stores the pass type template images in a unique folder

    based on the content type and object_id
    """
    return f"{instance._meta.app_label}/{instance._meta.model.__name__}/{instance.name}/template-image/{filename}"


def pass_type_concession_template_image_path(instance, filename):
    """Stores the pass type concession template images in a unique folder

    based on the content type and object_id
    """
    return (
        f"{instance._meta.app_label}/{instance._meta.model.__name__}/{instance.name}"
        f"/concession/template-image/{filename}"
    )


class PassType(models.Model):
    """A class to represent a pass type"""

    slug = AutoSlugField(unique=True, populate_from="display_name")
    image = ResizedImageField(
        size=[300, 150],
        quality=99,
        upload_to=pass_type_image_path,
        help_text="Ideal dimension for image are 300px (width) x 150px (height)",
        null=False,
        blank=False,
    )
    template_image = ResizedImageField(
        size=[540, 225],
        quality=99,
        upload_to=pass_type_template_image_path,
        help_text="Ideal dimension for image are 540px (width) x 225px (height)",
        null=True,
        blank=False,
    )
    concession_template_image = ResizedImageField(
        size=[540, 225],
        quality=99,
        upload_to=pass_type_concession_template_image_path,
        help_text="Ideal dimension for image are 540px (width) x 225px (height)",
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=100, editable=False
    )  # Name reserved for system use
    display_name = models.CharField(max_length=50, null=False, blank=False)
    display_name_colour = ColorField(
        default="#000000",
        help_text="Choose a colour for the pass type heading on the pass template.",
        null=False,
        blank=False,
    )
    concession_display_name_colour = ColorField(
        default="#000000",
        help_text="Choose a colour for the concession pass type heading on the pass template.",
        null=False,
        blank=False,
    )
    description = RichTextField(null=True)
    oracle_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Only to be used for pass types that are not district or park group specific. I.e. Pinjar Pass.",
        null=True,
        blank=True,
    )
    can_be_renewed_automatically = models.BooleanField(
        null=False, blank=False, default=False
    )
    display_order = models.SmallIntegerField(null=False, blank=False)
    display_retailer = models.BooleanField(null=False, blank=False, default=True)
    display_externally = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Pass Type"
        verbose_name_plural = "Pass Types"
        ordering = ["id"]

    def __str__(self):
        return f"{self.display_name}"

    def get_default_pricing_window(self):
        return PassTypePricingWindow.objects.filter(
            pass_type=self, date_expiry__isnull=True
        ).first()

    @classmethod
    def get_default_options_by_pass_type_id(self, pass_type_id):
        default_pricing_window = (
            PassTypePricingWindow.get_default_pricing_window_by_pass_type_id(
                pass_type_id
            )
        )
        options = PassTypePricingWindowOption.objects.filter(
            pricing_window=default_pricing_window
        ).count()
        if 0 == options:
            logger.critical(
                "CRITICAL: There are no options for pricing window : {} for pass type {}".format(
                    default_pricing_window.name, default_pricing_window.pass_type.name
                )
            )
            raise NoDefaultPricingWindowExists(
                "CRITICAL: There are no options for pricing window : {} for pass type {}".format(
                    default_pricing_window.name, default_pricing_window.pass_type.name
                )
            )
        else:
            return PassTypePricingWindowOption.objects.filter(
                pricing_window=default_pricing_window
            )

    @classmethod
    def check_required_pass_types_exist(cls, messages, critical_issues):
        pass_types_missing = False
        for pass_type in settings.PASS_TYPES:
            if not PassType.objects.filter(name=pass_type[0]).exists():
                pass_types_missing = True
                critical_issues.append(
                    "CRITICAL: Pass type with name {} does not exist.".format(
                        pass_type[0]
                    )
                )
        if not pass_types_missing:
            messages.append("SUCCESS: All required pass types exist.")


class PassTypePricingWindowManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("pass_type")


class PassTypePricingWindow(models.Model):
    """A class to represent a pass type pricing window

    The default pricing window for a pass type will have no expiry date
    The system will not allow for each pass type to have more than one
    default pricing window.
    """

    objects = PassTypePricingWindowManager()

    name = models.CharField(max_length=50, null=False, blank=False)
    pass_type = models.ForeignKey(
        PassType,
        on_delete=models.PROTECT,
        related_name="pricing_window",
        null=False,
        blank=False,
    )
    date_start = models.DateField()
    date_expiry = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Pricing Window"
        ordering = ["pass_type", "date_start", "date_expiry"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.date_expiry:
            default_pricing_window_count = (
                PassTypePricingWindow.objects.filter(
                    pass_type=self.pass_type,
                    date_expiry__isnull=True,
                )
                .exclude(pk=self.pk)
                .count()
            )
            if default_pricing_window_count > 0:
                raise ValidationError(
                    "There can only be one default pricing window for a pass type. \
                    Default pricing windows are those than have no expiry date."
                )
            else:
                if self.date_start > timezone.now().date():
                    raise ValidationError(
                        "The default pricing window start date must be in the past."
                    )
        else:
            if self.date_start >= self.date_expiry:
                raise ValidationError(
                    "The start date must occur before the expiry date."
                )
            if self.date_expiry <= timezone.now().date():
                raise ValidationError("The expiry date must be in the future.")

        super().save(*args, **kwargs)

    @property
    def is_default(cls):
        # If there is no expiry date then it is the default pricing window
        return not cls.date_expiry

    @property
    def status(self):
        if not self.date_expiry:
            return "Current"
        if self.date_start > timezone.now().date():
            return "Future"
        elif self.date_expiry <= timezone.now().date():
            return "Expired"
        else:
            return "Current"

    @classmethod
    def get_default_pricing_window_by_pass_type_id(self, pass_type_id):
        try:
            default_pricing_window = PassTypePricingWindow.objects.get(
                pass_type__id=pass_type_id, date_expiry__isnull=True
            )
        except ObjectDoesNotExist:
            logger.critical(
                f"CRITICAL: There is no default pricing window for pass type with id: {pass_type_id}"
            )
            raise NoDefaultPricingWindowExists(
                f"CRITICAL: There is no default pricing window for pass type with id: {pass_type_id}"
            )
        except MultipleObjectsReturned:
            logger.critical(
                f"CRITICAL: There is more than one default pricing window for pass type with id: {pass_type_id}"
            )
            raise MultipleDefaultPricingWindowsExist(
                f"CRITICAL: There is more than one default pricing window for pass type with id: {pass_type_id}"
            )
        return default_pricing_window

    @classmethod
    def check_default_pricing_windows(self, messages, critical_issues):
        pass_types = PassType.objects.all()
        for pass_type in pass_types:
            default_pricing_window_count = PassTypePricingWindow.objects.filter(
                pass_type__id=pass_type.id, name="Default"
            ).count()
            if 1 == default_pricing_window_count:
                messages.append(
                    f"SUCCESS: There is one default pricing window for pass type {pass_type.name}"
                )
            elif 0 == default_pricing_window_count:
                critical_issues.append(
                    f"CRITICAL: There is no default pricing window for pass type  {pass_type.name}"
                )
            else:
                critical_issues.append(
                    f"CRITICAL: There is more than one default pricing window for pass type {pass_type.name}"
                )

    def is_valid(self):
        if not self.date_expiry and settings.PRICING_WINDOW_DEFAULT_NAME == self.name:
            """The default pricing window is always valid as it forms the template that other pricing windows
            must follow"""
            return True
        else:
            default_pricing_window = (
                PassTypePricingWindow.get_default_pricing_window_by_pass_type_id(
                    self.pass_type.id
                )
            )
            if sorted(list(self.options.values_list("name", "duration"))) == sorted(
                list(default_pricing_window.options.values_list("name", "duration"))
            ):
                return True
            else:
                return False


class PassTypePricingWindowOptionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("pricing_window", "pricing_window__pass_type")
        )


class PassTypePricingWindowOption(models.Model):
    """A class to represent a pass type pricing window option"""

    objects = PassTypePricingWindowOptionManager()

    pricing_window = models.ForeignKey(
        PassTypePricingWindow, on_delete=models.CASCADE, related_name="options"
    )
    name = models.CharField(max_length=50)  # i.e. '5 days'
    duration = models.SmallIntegerField()  # in days i.e. 5, 14, 28, 365
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Duration Option"
        verbose_name_plural = "Duration Options"
        ordering = ["pricing_window", "price"]

    def __str__(self):
        return f"{self.pricing_window.pass_type.display_name} - {self.name} \
            (Pricing Window: {self.pricing_window.name})"

    @classmethod
    def get_options_by_pass_type_and_date(self, pass_type_id, date):
        return self.get_current_options_by_pass_type_id(pass_type_id, date)

    @classmethod
    def get_current_options_by_pass_type_id(self, pass_type_id, date=None):
        try:
            pass_type = PassType.objects.get(id=pass_type_id)
        except ObjectDoesNotExist:
            logger.info(f"No Pass Type Exists with ID: {pass_type_id}.")
            return []

        pricing_windows_for_pass = PassTypePricingWindow.objects.filter(
            pass_type=pass_type
        )

        if date:
            pricing_windows_for_pass.filter(date_start__lte=date, date_expiry__gte=date)

        pricing_windows_for_pass_count = pricing_windows_for_pass.count()

        if 0 == pricing_windows_for_pass_count:
            logger.critical(
                "CRITICAL: There is no default pricing window for Pass Type: {}.".format(
                    pass_type
                )
            )
            return []
        # If there is only one pricing window for the pass type it must be the default
        if 1 == PassTypePricingWindow.objects.filter(pass_type=pass_type).count():
            pricing_window = PassTypePricingWindow.objects.get(pass_type=pass_type)
        else:
            # Get any pricing windows that are currently valid excluding the default pricing window
            current_pricing_window_count = (
                PassTypePricingWindow.objects.exclude(date_expiry__isnull=True)
                .filter(
                    pass_type=pass_type,
                    date_start__lte=timezone.now(),
                    date_expiry__gte=timezone.now(),
                )
                .count()
            )

            # If there are none just get the default pricing window
            if 0 == current_pricing_window_count:
                pricing_window = PassTypePricingWindow.objects.get(
                    pass_type=pass_type, date_expiry__isnull=True
                )

            elif 1 == current_pricing_window_count:
                pricing_window = PassTypePricingWindow.objects.exclude(
                    date_expiry__isnull=True
                ).get(
                    pass_type=pass_type,
                    date_start__lte=timezone.now(),
                    date_expiry__gte=timezone.now(),
                )
            else:
                # When there are two or more currently valid pricing windows we return the window that
                # started the most recently And log a warning so that admins can be alerted to this.
                # Validation shouldn't allow this sitation to occur but ... just in case.
                logger.warning(
                    f"WARNING: There are more than one currently valid pricing windows for Pass Type: {pass_type}"
                )
                pricing_window = (
                    PassTypePricingWindow.objects.exclude(date_expiry__isnull=True)
                    .filter(
                        pass_type=pass_type,
                        date_start__lte=timezone.now(),
                        date_expiry__gte=timezone.now(),
                    )
                    .order_by("date_start")
                    .last()
                )

        return PassTypePricingWindowOption.objects.filter(pricing_window=pricing_window)

    @classmethod
    def get_default_options_by_pass_type_id(self, pass_type_id):
        return PassTypePricingWindowOption.objects.filter(
            pricing_window__name=settings.PRICING_WINDOW_DEFAULT_NAME,
            pricing_window__date_expiry__isnull=True,
            pricing_window__pass_type__id=pass_type_id,
        )

    def get_default_option(self):
        """Due to the way the system determines which oracle code for use for a park pass
        we need to be able to get the default option for any option

        The default option is the option from the default pricing window (for a pass type)
        that has the same duration as this option (self).
        .
        """
        if self.pricing_window.is_default:
            # The option passed is an option from the default pricing window so just return it
            return self

        # Find the option from the default pricing window with the same duration as the option passed
        default_option = PassTypePricingWindowOption.objects.filter(
            duration=self.duration,
            pricing_window__date_expiry__isnull=True,
            pricing_window__pass_type=self.pricing_window.pass_type,
        )
        if default_option.exists():
            return default_option.first()

        error_message = f"No default option found for option: {self}"
        logger.critical(error_message)
        raise NoDefaultOptionFoundForOptionWindowExists(error_message)


def pass_template_file_path(instance, filename):
    """Stores the pass template documents in a unique folder

    based on the content type and object_id
    """
    return f"{instance._meta.app_label}/{instance._meta.model.__name__}/{instance.version}/{filename}"


upload_protected_files_storage = FileSystemStorage(
    location=settings.PROTECTED_MEDIA_ROOT, base_url="/protected_media"
)


class PassTemplate(models.Model):
    """A class to represent a pass template

    The template file field will be the word document that is used as a template to generate a park pass.

    If pass_type is specified then passes of that type will use that template.

    If pass_type is not specified (null) then any pass type that does not have a template specified
    will use this template.

    The highest version number will be the template that is used to generate passes.
    """

    template = models.FileField(
        upload_to=pass_template_file_path,
        storage=upload_protected_files_storage,
        null=False,
        blank=False,
    )
    pass_type = models.ForeignKey(
        PassType,
        on_delete=models.PROTECT,
        related_name="pass_template",
        help_text="When left blank this template will be used for all pass types that don't have a template specified.",
        null=True,
        blank=True,
    )
    version = models.SmallIntegerField(null=False, blank=False)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Pass Template"
        verbose_name_plural = "Pass Templates"
        unique_together = (("pass_type", "version"),)

    def __str__(self):
        return f"{self.template.name} (Version: {self.version}) (Size: {self.pretty_size()})"

    @classmethod
    def get_template_by_pass_type(cls, pass_type):
        template = cls.objects.filter(pass_type=pass_type).order_by("-version").first()
        if template:
            return template
        return cls.objects.filter(pass_type__isnull=True).order_by("-version").first()

    def pretty_size(self):
        size_bytes = self.template.size
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"


class PassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "option",
                "option__pricing_window",
                "option__pricing_window__pass_type",
                "sold_via",
                "cancellation",
            )
        )


class Pass(models.Model):
    """A class to represent a pass"""

    objects = PassManager()

    NEW_SOUTH_WALES = "NSW"
    VICTORIA = "VIC"
    QUEENSLAND = "QLD"
    WESTERN_AUSTRALIA = "WA"
    SOUTH_AUSTRALIA = "SA"
    TASMANIA = "TAS"
    AUSTRALIAN_CAPITAL_TERRITORY = "ACT"
    NORTHERN_TERRITORY = "NT"

    STATE_CHOICES = [
        (NEW_SOUTH_WALES, "Western Australia"),
        (VICTORIA, "Victoria"),
        (QUEENSLAND, "Queensland"),
        (WESTERN_AUSTRALIA, "Western Australia"),
        (SOUTH_AUSTRALIA, "South Australia"),
        (TASMANIA, "Tasmania"),
        (AUSTRALIAN_CAPITAL_TERRITORY, "Australian Capital Territory"),
        (NORTHERN_TERRITORY, "Western Australia"),
    ]

    FUTURE = "FU"
    CURRENT = "CU"
    EXPIRED = "EX"
    CANCELLED = "CA"
    VALID = "VA"
    AWAITING_AUTO_RENEWAL = "AR"
    PROCESSING_STATUS_CHOICES = [
        (CANCELLED, "Cancelled"),
        (AWAITING_AUTO_RENEWAL, "Awaiting Auto Renewal"),
        (VALID, "Valid"),
    ]

    user = models.IntegerField(null=True, blank=True)  # EmailUserRO
    option = models.ForeignKey(PassTypePricingWindowOption, on_delete=models.PROTECT)
    pass_number = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    mobile = models.CharField(max_length=10, null=False, blank=False, default="")
    company = models.CharField(max_length=50, null=True, blank=True)
    address_line_1 = models.CharField(max_length=100, null=True, blank=True)
    address_line_2 = models.CharField(max_length=100, null=True, blank=True)
    suburb = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(
        max_length=3,
        choices=STATE_CHOICES,
        default=WESTERN_AUSTRALIA,
        null=True,
        blank=True,
    )
    postcode = models.CharField(
        null=True,
        blank=True,
        max_length=4,
        validators=[
            MinLengthValidator(4, "Australian postcodes must contain 4 digits")
        ],
    )
    rac_member_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_registration_1 = models.CharField(max_length=10, null=True, blank=True)
    vehicle_registration_2 = models.CharField(max_length=10, null=True, blank=True)
    drivers_licence_number = models.CharField(max_length=11, null=True, blank=True)
    park_group = models.ForeignKey(
        ParkGroup, on_delete=models.PROTECT, null=True, blank=True
    )
    date_start = models.DateField(null=False, blank=False)
    date_expiry = models.DateField(null=False, blank=False)
    renew_automatically = models.BooleanField(null=False, blank=False, default=False)
    park_pass_renewed_from = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        related_name="renewed_pass",
        null=True,
        blank=True,
    )
    prevent_further_vehicle_updates = models.BooleanField(
        null=False, blank=False, default=False
    )
    park_pass_pdf = models.FileField(
        storage=upload_protected_files_storage, null=True, blank=True, max_length=500
    )
    processing_status = models.CharField(
        max_length=2, choices=PROCESSING_STATUS_CHOICES, null=True, blank=True
    )
    in_cart = models.BooleanField(null=False, blank=False, default=True)
    purchase_email_sent = models.BooleanField(null=False, blank=False, default=False)
    sold_via = models.ForeignKey(
        RetailerGroup, on_delete=models.PROTECT, null=True, blank=True
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "Passes"
        ordering = ["-datetime_created"]

    def __str__(self):
        if self.pass_number:
            return f"{self.pass_number}"
        return "Pass number not yet assigned."

    @property
    def email_user(self):
        return retrieve_email_user(self.user)

    @property
    def pricing_window(self):
        return self.option.pricing_window.name

    @property
    def price(self):
        return self.option.price

    @property
    def pass_type(self):
        return self.option.pricing_window.pass_type.display_name

    @property
    def is_gold_star_pass(self):
        return settings.GOLD_STAR_PASS == self.option.pricing_window.pass_type.name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def price_after_concession_applied(self):
        if hasattr(self, "concession_usage"):
            concession = self.concession_usage.concession
            discount_amount = concession.discount_as_amount(self.price)
            price_after_discount = self.price - discount_amount
            return price_after_discount
        return self.price

    @property
    def price_after_rac_discount_applied(self):
        if hasattr(self, "rac_discount_usage"):
            return (
                self.price_after_concession_applied
                - self.rac_discount_usage.discount_amount
            )
        return self.price_after_concession_applied

    @property
    def price_after_discount_code_applied(self):
        if hasattr(self, "discount_code_usage"):
            discount_code = self.discount_code_usage.discount_code
            discount_amount = discount_code.discount_as_amount(
                self.price_after_rac_discount_applied
            )
            price_after_discount = (
                self.price_after_rac_discount_applied - discount_amount
            )
            return price_after_discount
        return self.price_after_rac_discount_applied

    @property
    def price_after_voucher_applied(self):
        if hasattr(self, "voucher_transaction"):
            voucher_transaction_balance = self.voucher_transaction.balance()
            return self.price_after_discount_code_applied + voucher_transaction_balance
        return self.price_after_discount_code_applied

    @property
    def price_after_all_discounts(self):
        """Convenience method that makes more descriptive sense"""
        return self.price_after_voucher_applied.quantize(Decimal("0.00"))

    @property
    def price_display(self):
        return f"${self.price_after_all_discounts}"

    @property
    def gst(self):
        gst_calcuation = Decimal(100 / (100 + int(settings.LEDGER_GST)))
        return Decimal(
            self.price_after_all_discounts
            - (self.price_after_all_discounts * gst_calcuation)
        ).quantize(Decimal("0.00"))

    @property
    def gst_display(self):
        return f"${self.gst}"

    @property
    def pro_rata_refund_amount_display(self):
        return f"${self.pro_rata_refund_amount()}"

    @property
    def status(self):
        if self.in_cart and self.park_pass_renewed_from:
            return Pass.AWAITING_AUTO_RENEWAL
        elif self.is_cancelled:
            return Pass.CANCELLED
        elif self.date_start > timezone.now().date():
            return Pass.FUTURE
        elif self.date_expiry <= timezone.now().date():
            return Pass.EXPIRED
        else:
            return Pass.CURRENT

    @property
    def status_display(self):
        if self.is_cancelled:
            return "Cancelled"
        elif self.date_start > timezone.now().date():
            return "Future"
        elif self.date_expiry <= timezone.now().date():
            return "Expired"
        else:
            return "Current"

    @property
    def is_cancelled(self):
        return hasattr(self, "cancellation")

    @property
    def has_expired(self):
        return self.date_expiry <= timezone.now().date()

    @property
    def get_next_renewal_option(self):
        """Customers are sent an email settings.PASS_REMINDER_DAYS_PRIOR to the autorenewal to
        let them know how much the charge to their card will be. This is needed because the system
        has dynamic pricing windows and if we didn't lock the price in at the time of the reminder
        then the customer would have no warning of exactly how much their card was going to charged ."""
        if not self.renew_automatically:
            return None

        reminder_date = self.date_expiry - timezone.timedelta(
            days=settings.PASS_REMINDER_DAYS_PRIOR
        )
        options = PassTypePricingWindowOption.get_options_by_pass_type_and_date(
            self.option.pricing_window.pass_type.id, reminder_date
        )
        return options.filter(duration=self.option.duration).first()

    @property
    def get_next_renewal_price(self):
        option = self.get_next_renewal_option
        if hasattr(self, "concession_usage"):
            concession = self.concession_usage.concession
            discount_amount = concession.discount_as_amount(option.price)
            return option.price - discount_amount
        return option.price

    @property
    def order(self):
        content_type = ContentType.objects.get_for_model(self)
        if OrderItem.objects.filter(
            content_type=content_type, object_id=self.id
        ).exists():
            return OrderItem.objects.get(
                content_type=content_type, object_id=self.id
            ).order
        logger.warning("Can't find order for park pass: %s", self)
        return None

    @property
    def sold_internally(self):
        # Returns true for passes sold via the website and via internal retailers
        return (
            settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
            == self.sold_via.ledger_organisation
            or self.sold_via.is_internal_retailer
        )

    @property
    def invoice_link(self):
        if self.order:
            return self.order.invoice_link

    def pro_rata_refund_percentage(self):
        if self.date_start >= timezone.now().date():
            return 100
        if self.date_expiry <= timezone.now().date():
            return 0
        duration = self.option.duration
        delta = timezone.now().date() - self.date_start
        days_used = delta.days
        days_remaining = self.option.duration - days_used
        return round(days_remaining * 100 / duration)

    def pro_rata_refund_amount(self):
        amount = self.price_after_all_discounts * Decimal(
            self.pro_rata_refund_percentage() / 100
        )
        return Decimal(amount).quantize(Decimal("0.00"))

    def generate_qrcode(self):
        logger.info(f"Generating qr code for pass {self.pass_number}.")
        from parkpasses.components.passes.serializers import (
            ExternalQRCodePassSerializer,
        )

        qr = qrcode.QRCode(box_size=2)
        serializer = ExternalQRCodePassSerializer(self)
        logger.debug(f"serializer.data: {serializer.data}")
        request_json = {
            "data": f"{serializer.data}",
            "group": settings.ENCRYPTION_SERVER_GROUP,
        }
        request_url = settings.ENCRYPTION_SERVER_API_URL.format(
            settings.ENCRYPTION_SERVER_API_KEY
        )
        response = requests.post(request_url, data=request_json)
        logger.info("request_url: %s", request_url)
        if 200 != response.status_code:
            error_message = (
                f"Error encrypting qr code data for pass: {self.pass_number}. "
                f"response.status_code {response.status_code}, response.content: {response.content}"
            )
            logger.error(error_message)
            raise QRCodeEncryptionFailed(error_message)
        encrypted_pass_data = response.json()["data"]
        logger.info("encrypted_pass_data: %s", encrypted_pass_data)
        qr.add_data(encrypted_pass_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill="black", back_color="white")
        qr_image_path = f"{settings.PROTECTED_MEDIA_ROOT}/{self._meta.app_label}/"
        qr_image_path += f"{self._meta.model.__name__}/passes/{self.user}/{self.pk}"
        if not os.path.exists(qr_image_path):
            os.makedirs(qr_image_path)
        logger.info(
            f"Saving qr code for pass {self.pass_number} to {qr_image_path}/qr_image.png."
        )
        qr_image.save(f"{qr_image_path}/qr_image.png")
        logger.info(f"Qr code for pass {self.pass_number} saved.")
        return f"{qr_image_path}/qr_image.png"

    def generate_park_pass_pdf(self):
        logger.info(f"Generating pdf for pass {self.pass_number}.")
        if not PassTemplate.objects.count():
            logger.critical(
                "CRITICAL: The system can not find a Pass Template to use for generating park passes.",
            )
            raise PassTemplateDoesNotExist(
                "CRITICAL: The system can not find a Pass Template to use for generating park passes."
            )
        qr_code_path = self.generate_qrcode()
        pass_type = self.option.pricing_window.pass_type
        pass_template = PassTemplate.get_template_by_pass_type(pass_type)
        pass_utils = PassUtils()
        safe_template_path = "/parkpasses/PassTemplate/"
        pass_template_path = os.path.normpath(f"/{pass_template.template.name}")
        if (
            os.path.commonprefix(
                (os.path.realpath(pass_template_path), safe_template_path)
            )
            != safe_template_path
        ):
            raise ValueError("Unsafe path detected in pass_template_path")
        pass_utils.generate_pass_pdf_from_docx_template(
            self, pass_template_path, qr_code_path
        )

    def imaginary_encryption_endpoint(self, json_pass_data):
        return json_pass_data

    def can_cancel_automatic_renewal(self):
        return self.date_expiry > timezone.now() + timezone.timedelta(days=1)

    def cancel_automatic_renewal(self):
        if not self.renew_automatically:
            raise ValidationError("This pass does not have automatic renewal enabled.")
        elif not self.can_cancel_automatic_renewal():
            raise ValidationError(
                "You must cancel automatic renewal of a pass at least 24 hours before the pass is due to renew."
            )
        else:
            self.renew_automatically = False
            self.save(update_fields=["renew_automatically"])
            logger.info(
                "Automatic renewal of pass {} has been cancelled.".format(
                    self.pass_number
                )
            )

    def set_processing_status(self):
        logger.info(f"Setting processing status for park pass: {self}.")
        if self.in_cart and self.park_pass_renewed_from:
            self.processing_status = Pass.AWAITING_AUTO_RENEWAL
            logger.info(
                f"Processing status set as: {Pass.AWAITING_AUTO_RENEWAL}.",
            )
        elif PassCancellation.objects.filter(park_pass=self).count():
            self.processing_status = Pass.CANCELLED
            logger.info(
                f"Processing status set as: {Pass.CANCELLED}.",
            )
        else:
            self.processing_status = Pass.VALID
            logger.info(
                f"Processing status set as: {Pass.VALID}.",
            )

    def save(self, *args, **kwargs):
        logger.info(f"Save pass called for park pass: {self}.")
        self.date_expiry = self.date_start + timezone.timedelta(
            days=self.option.duration
        )
        logger.info(f"Pass expiry date set as: {self.date_expiry}.")

        self.set_processing_status()

        # if self.user:
        #     logger.info(
        #         f"Pass has a user id: {self.user}",
        #     )
        #     email_user = self.email_user
        #     self.first_name = email_user.first_name
        #     self.last_name = email_user.last_name
        #     self.email = email_user.email
        #     logger.info(
        #         "Populated pass details from ledger email user.",
        #     )

        logger.info(f"Saving park pass: {self}")
        super().save(*args, **kwargs)
        logger.info(f"Park pass: {self} saved.")

        if not self.pass_number:
            logger.info(
                "Park pass does not yet have a pass number.",
            )
            self.pass_number = f"PP{self.pk:06d}"
            logger.info(
                f"Park pass assigned pass number: {self.pass_number}.",
            )

        if not Pass.CANCELLED == self.processing_status and not self.has_expired:
            if not self.in_cart:
                logger.info(
                    "Park pass has not been cancelled and is not in cart so generating park pass pdf.",
                )

                """Consider: Running generate_park_pass_pdf() with a message queue would be much better"""
                self.generate_park_pass_pdf()

                logger.info(
                    "Park pass pdf generated.",
                )

                if not self.purchase_email_sent:
                    logger.info(
                        "Park pass purchase email has not yet been sent.",
                    )
                    self.send_purchased_notification_email()
                    logger.info(
                        f"Pass purchased notification email sent for pass {self.pass_number}",
                    )
                    self.purchase_email_sent = True
                    logger.info(
                        "Assigning purchase email as sent.",
                    )

                else:
                    logger.info(
                        "Park pass purchase email has already been sent.",
                    )
                    self.send_updated_notification_email()
                    logger.info(
                        f"Pass update notification email sent for pass {self.pass_number}",
                    )

        logger.info(f"Updating park pass: {self}.")
        super().save(force_update=True)
        logger.info("Park pass updated.")

    def send_no_primary_card_for_autorenewal_email(self):
        error_message = "An exception occured trying to run "
        error_message += "send_no_primary_card_for_autorenewal_email for Pass with id {}. Exception {}"
        try:
            PassEmails.send_no_primary_card_for_autorenewal_email(self)
        except Exception as e:
            raise SendNoPrimaryCardForAutoRenewalEmailFailed(
                error_message.format(self.id, e)
            )

    def send_autorenew_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += (
            "send_autorenew_notification_email for Pass with id {}. Exception {}"
        )
        try:
            PassEmails.send_pass_autorenew_notification_email(self)
        except Exception as e:
            raise SendPassAutoRenewNotificationEmailFailed(
                error_message.format(self.id, e)
            )

    def send_autorenew_success_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += "send_autorenew_success_notification_email for Pass with id {}. Exception {}"
        try:
            PassEmails.send_pass_autorenew_success_notification_email(self)
        except Exception as e:
            raise SendPassAutoRenewSuccessNotificationEmailFailed(
                error_message.format(self.id, e)
            )

    def send_autorenew_failure_notification_email(self, failure_count):
        error_message = "An exception occured trying to run "
        error_message += "send_autorenew_failure_notification_email for Pass with id {}. Exception {}"
        try:
            PassEmails.send_pass_autorenew_failure_notification_email(
                self, failure_count
            )
        except Exception as e:
            raise SendPassAutoRenewFailureNotificationEmailFailed(
                error_message.format(self.id, e)
            )

    def send_final_autorenewal_failure_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += "send_final_autorenewal_failure_notification_email for Pass with id {}. Exception {}"
        try:
            PassEmails.send_pass_final_autorenew_failure_notification_email(self)
        except Exception as e:
            raise SendPassFinalAutoRenewFailureNotificationEmailFailed(
                error_message.format(self.id, e)
            )

    def send_expiry_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += (
            "send_expiry_notification_email for Pass with id {}. Exception {}"
        )
        try:
            PassEmails.send_pass_expiry_notification_email(self)
        except Exception as e:
            raise SendPassExpiryNotificationEmailFailed(
                error_message.format(self.id, e)
            )

    def send_expired_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += (
            "send_expired_notification_email for Pass with id {}. Exception {}"
        )
        try:
            PassEmails.send_pass_expired_notification_email(self)
        except Exception as e:
            raise SendPassExpiredNotificationEmailFailed(
                error_message.format(self.id, e)
            )

    def send_purchased_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += (
            "send_purchased_notification_email for Pass with id {}. Exception {}"
        )
        try:
            PassEmails.send_pass_purchased_notification_email(self)
        except Exception as e:
            raise SendPassPurchasedEmailNotificationFailed(
                error_message.format(self.id, e)
            )

    def send_updated_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += (
            "send_updated_notification_email for Pass with id {}. Exception {}"
        )
        try:
            PassEmails.send_pass_updated_notification_email(self)
        except Exception as e:
            raise SendPassPurchasedEmailNotificationFailed(
                error_message.format(self.id, e)
            )

    def send_vehicle_details_not_yet_provided_notification_email(self):
        error_message = "An exception occured trying to run "
        error_message += (
            "send_purchased_notification_email for Pass with id {}. Exception {}"
        )
        try:
            PassEmails.send_pass_vehicle_details_not_yet_provided_notification_email(
                self
            )
        except Exception as e:
            raise SendPassVehicleDetailsNotYetProvidedEmailNotificationFailed(
                error_message.format(self.id, e)
            )


class PassCancellationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("park_pass")


class PassCancellation(models.Model):
    """A class to represent a pass cancellation

    A one to one related model to store the cancellation reason

    Also, will be able to have a list of files attached to it to justify/explain
    the cancellation"""

    objects = PassCancellationManager()

    park_pass = models.OneToOneField(
        Pass, on_delete=models.PROTECT, related_name="cancellation"
    )
    cancellation_reason = models.TextField(null=False, blank=False)
    datetime_cancelled = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "Pass Cancellations"

    def __str__(self):
        return f"Cancellation for Pass: {self.park_pass.pass_number} (Date Cancelled: {self.datetime_cancelled})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.park_pass.processing_status = Pass.CANCELLED
        self.park_pass.save()

    def delete(self, *args, **kwargs):
        """If the pass cancellation is deleted we automatically recalculate the status"""
        park_pass = self.park_pass
        deleted = super().delete()
        park_pass.set_processing_status()
        park_pass.save()
        return deleted


class PassAutoRenewalAttemptManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("park_pass")


class PassAutoRenewalAttempt(models.Model):
    objects = PassAutoRenewalAttemptManager()

    park_pass = models.ForeignKey(
        Pass, on_delete=models.PROTECT, related_name="auto_renewal_attempts"
    )
    auto_renewal_succeeded = models.BooleanField(null=False, blank=False, default=False)
    datetime_attempted = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "Pass Auto Renewal Attempts"

    def __str__(self):
        status = "Succeeded" if self.auto_renewal_succeeded else "Failed"
        return f"Auto Renewal Attempt for Pass: {self.park_pass.pass_number} {status} at {self.datetime_attempted}"


class RACDiscountUsageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("park_pass")


class RACDiscountUsage(models.Model):
    """When an RAC discount is used to purchase a pass we create an rac discount usage
    record. This can be used to determine if an RAC discount should be applied to passes
    that are auto renewing.
    """

    objects = RACDiscountUsageManager()

    park_pass = models.OneToOneField(
        Pass,
        on_delete=models.PROTECT,
        related_name="rac_discount_usage",
        null=False,
        blank=False,
    )

    discount_percentage = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        blank=True,
        null=True,
        validators=PERCENTAGE_VALIDATOR,
    )

    def __str__(self):
        return (
            "RAC Discount ("
            + str(self.discount_percentage)
            + "% Off)"
            + " used to purchase park pass "
            + self.park_pass.pass_number
        )

    @property
    def discount_amount(self):
        discount_amount = Decimal(
            self.park_pass.price_after_concession_applied
            * (self.discount_percentage / 100)
        )
        return discount_amount.quantize(Decimal("0.01"))

    class Meta:
        app_label = "parkpasses"


class DistrictPassTypeDurationOracleCode(models.Model):
    district = models.ForeignKey(
        District,
        related_name="district_pass_type_duration_oracle_code",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Leave blank for PICA oracle codes (online sales)",
    )
    option = models.ForeignKey(
        PassTypePricingWindowOption,
        on_delete=models.CASCADE,
        related_name="district_oracle_code",
    )
    oracle_code = models.CharField(
        max_length=80,
        null=False,
        blank=False,
        help_text="The oracle code to be used for this district, pass type and pass duration.",
    )

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Oracle Code"
        verbose_name_plural = "Oracle Codes"
        unique_together = (("district", "option"),)
        ordering = (
            "district__name",
            "option__pricing_window__pass_type__display_order",
            "option__duration",
        )

    def __str__(self):
        district_name = settings.PICA_ORACLE_CODE_LABEL
        if self.district:
            district_name = self.district.name
        return (
            f"{district_name} - "
            f"{self.option.pricing_window.pass_type.display_name} - "
            f"{self.option.name} - {self.oracle_code}"
        )

    @classmethod
    def check_necessary_district_based_oracle_codes_exist(
        cls, messages, critical_issues
    ):
        for pass_type in PassType.objects.filter(
            oracle_code__isnull=True, display_externally=True, display_retailer=True
        ):
            default_pricing_window = pass_type.get_default_pricing_window()
            for option in default_pricing_window.options.all():
                pica_oracle_code = cls.objects.filter(
                    district__isnull=True, option=option
                )
                if not pica_oracle_code.exists():
                    critical_issues.append(
                        f"CRITICAL: There is no PICA oracle code for {pass_type.display_name} - {option.name}. "
                        "Please run the oracle_codes_create_initial_records management command to "
                        "generate the required codes."
                    )
                    return
                for district in District.objects.filter(archive_date__isnull=True):
                    district_based_oracle_code = cls.objects.filter(
                        district=district, option=option
                    )
                    if not district_based_oracle_code.exists():
                        critical_issues.append(
                            "CRITICAL: There is no oracle code for "
                            f"{district.name} - {pass_type.display_name} - {option.name}. "
                            "Please run the oracle_codes_create_initial_records management "
                            "command to generate the required codes."
                        )
                        return
        messages.append("SUCCESS: All necessary district-based oracle codes exist.")

    @classmethod
    def check_oracle_codes_have_been_entered(cls, messages, critical_issues):
        district_based_oracle_codes = cls.objects.all()
        if 0 == district_based_oracle_codes.count():
            critical_issues.append(
                "CRITICAL: There are no district-based oracle codes. "
                "Please run the oracle_codes_create_initial_records management command to generate the required codes."
            )
            return
        unentered_oracle_codes = cls.objects.filter(
            oracle_code=settings.UNENTERED_ORACLE_CODE_LABEL
        )
        if unentered_oracle_codes.exists():
            critical_issues.append(
                f"There are {unentered_oracle_codes.count()} district-based oracle codes that have not been entered."
            )
        else:
            messages.append(
                "SUCCESS: All district-based oracle codes have been entered."
            )
