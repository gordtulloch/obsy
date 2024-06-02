from django.contrib import admin
from .models import fitsFile,fitsHeader

class fitsFileAdmin(admin.ModelAdmin):
    list_display = ("fitsFileId","date","filename",)
    
class fitsHeaderAdmin(admin.ModelAdmin):
    list_display = ("fitsHeaderId","parentUUID","keyword","value",)
    
admin.site.register(fitsFile,fitsFileAdmin)
admin.site.register(fitsHeader,fitsHeaderAdmin)