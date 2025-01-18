from django.contrib import admin
from .models import Target

class targetAdmin(admin.ModelAdmin):
    list_display = ("targetName","targetClass","targetType")
    
admin.site.register(Target, targetAdmin)