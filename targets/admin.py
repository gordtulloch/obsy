from django.contrib import admin
from .models import target,simbadType

class targetAdmin(admin.ModelAdmin):
    list_display = ("targetName","targetClass","targetType")
    
class simbadTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "description","category")

admin.site.register(target, targetAdmin)
admin.site.register(simbadType, simbadTypeAdmin)