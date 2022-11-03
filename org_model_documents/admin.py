from django.contrib import admin

from org_model_documents.models import Document


class DocumentAdmin(admin.ModelAdmin):
    model = Document
    list_display = (
        "object_id",
        "content_type",
        "_file",
        "datetime_created",
        "datetime_updated",
    )


admin.site.register(Document, DocumentAdmin)
