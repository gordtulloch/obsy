from django.contrib import admin
from .models import observatory,observer,telescope,imager

class observatoryAdmin(admin.ModelAdmin):
    list_display = ("observatoryId","name","shortname","longitude","latitude","tz")
    
class observerAdmin(admin.ModelAdmin):
    list_display = ("observerId","firstname","middlename","lastname","tz")
       
class telescopeAdmin(admin.ModelAdmin):
    list_display = ("telescopeId","name","shortname","telescopeType","aperture","focalLength",)
    
class currentConfigAdmin(admin.ModelAdmin):
    list_display = ("observatoryId","telescopeId", "imagerId",)

class imagerAdmin(admin.ModelAdmin):
    list_display = ("imagerId","name","shortname","imagerType","xDim","yDim","xPixelSize","yPixelSize",)
    
admin.site.register(observatory,observatoryAdmin)
admin.site.register(observer,observerAdmin)
admin.site.register(telescope,telescopeAdmin)
admin.site.register(imager,imagerAdmin)
