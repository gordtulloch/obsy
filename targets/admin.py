from django.contrib import admin
from .models import TargetModel

class TargetModelAdmin(admin.ModelAdmin):
    list_display = ("target", "catalogID")

admin.site.register(TargetModel, TargetModelAdmin)