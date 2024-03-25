from django.contrib import admin
from .models import target

class targetAdmin(admin.ModelAdmin):
    list_display = ("targetName", "catalogIDs")

admin.site.register(target, targetAdmin)