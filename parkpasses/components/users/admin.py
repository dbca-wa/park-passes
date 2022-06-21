from django.contrib import admin

from parkpasses.components.users.models import UserInformation


class UserInformationAdmin(admin.ModelAdmin):
    model = UserInformation
    list_display = ("user", "concession")


admin.site.register(UserInformation, UserInformationAdmin)
