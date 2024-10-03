from django.contrib import admin
from .models import observation

class observationAdmin(admin.ModelAdmin):
    list_display = ("targetName","targetType")
