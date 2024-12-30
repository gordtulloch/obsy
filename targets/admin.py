from django.contrib import admin
from .models import Target,SimbadType

class targetAdmin(admin.ModelAdmin):
    list_display = ("targetName","targetClass","targetType")
    
class simbadTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "description","targetClass")

admin.site.register(Target, targetAdmin)
admin.site.register(SimbadType, simbadTypeAdmin)