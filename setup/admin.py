from django.contrib import admin
from .models import fitsFile,fitsHeader,observatory,observer,instrument,instrument,telescope,imager

class fitsFileAdmin(admin.ModelAdmin):
    list_display = ("fitsFileId","date","filename",)
    
class fitsHeaderAdmin(admin.ModelAdmin):
    list_display = ("fitsHeaderId","parentUNID","keyword","value",)
    
class observatoryAdmin(admin.ModelAdmin):
    list_display = ("observatoryId","name","shortname","longitude","latitude","tz")
    
class observerAdmin(admin.ModelAdmin):
    list_display = ("observerId","firstname","middlename","lastname","tz")
    
class instrumentAdmin(admin.ModelAdmin):
    list_display = ("instrumentId","name","shortname","instType",)
    
class telescopeAdmin(admin.ModelAdmin):
    list_display = ("telescopeId","name","shortname","telescopeType","aperture","focalLength",)
    
class imagerAdmin(admin.ModelAdmin):
    list_display = ("imagerId","name","shortname","imagerType","xDim","yDim","xPixelSize","yPixelSize",)
    

admin.site.register(fitsFile,fitsFileAdmin)
admin.site.register(fitsHeader,fitsHeaderAdmin)
admin.site.register(observatory,observatoryAdmin)
admin.site.register(observer,observerAdmin)
admin.site.register(telescope,telescopeAdmin)
admin.site.register(instrument,instrumentAdmin)
admin.site.register(imager,imagerAdmin)