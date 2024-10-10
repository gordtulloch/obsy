from django.contrib import admin
from .models import currentConfig

class currentConfigAdmin(admin.ModelAdmin):
    list_display = ("observatoryId","telescopeId", "imagerId",)

admin.site.register(currentConfig,currentConfigAdmin)


