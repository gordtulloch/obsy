from django.contrib import admin
from .models import objectsCatalog,fitsFile,fitsHeader,observatory,observer,instrument,instrument,telescope,imager

class objectsCatalogAdmin(admin.ModelAdmin):
    list_display = ("objID","objName","objRA2000","objDec2000","objConst",)

class fitsFileAdmin(admin.ModelAdmin):
    list_display = ("thisUNID","date","filename",)
    
class fitsHeaderAdmin(admin.ModelAdmin):
    list_display = ("thisUNID","parentUNID","keyword","value",)
    
class observatoryAdmin(admin.ModelAdmin):
    list_display = ("name","shortname","longitude","latitude","tz")
    
class observerAdmin(admin.ModelAdmin):
    list_display = ("firstname","middlename","lastname","tz")
    
class instrumentAdmin(admin.ModelAdmin):
    list_display = ("name","shortname","instType",)
    
class telescopeAdmin(admin.ModelAdmin):
    list_display = ("name","shortname","telescopeType","aperture","focalLength",)
    
class imagerAdmin(admin.ModelAdmin):
    list_display = ("name","shortname","imagerType","xDim","yDim","xPixelSize","yPixelSize",)
    
admin.site.register(objectsCatalog,objectsCatalogAdmin)
admin.site.register(fitsFile,fitsFileAdmin)
admin.site.register(fitsHeader,fitsHeaderAdmin)
admin.site.register(observatory,observatoryAdmin)
admin.site.register(observer,observerAdmin)
admin.site.register(telescope,telescopeAdmin)
admin.site.register(instrument,instrumentAdmin)
admin.site.register(imager,imagerAdmin)