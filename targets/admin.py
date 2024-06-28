from django.contrib import admin
from .models import target,simbadType,scheduleMaster,scheduleDetail,sequenceFile,scheduleFile

class targetAdmin(admin.ModelAdmin):
    list_display = ("targetName","targetClass","targetType")
    
class scheduleMasterAdmin(admin.ModelAdmin):
    list_display = ("scheduleMasterId","userId","scheduleDate")
    
class scheduleDetailAdmin(admin.ModelAdmin):
    list_display = ("scheduleDetailId","scheduleMasterId","targetId")
    
class sequenceFileAdmin(admin.ModelAdmin):
    list_display = ("sequenceFileId","sequenceFileName")
    
class scheduleFileAdmin(admin.ModelAdmin):
    list_display = ("scheduleFileId","scheduleFileName")
    
class simbadTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "description","category")

admin.site.register(target, targetAdmin)
admin.site.register(scheduleMaster, scheduleMasterAdmin) 
admin.site.register(scheduleDetail, scheduleDetailAdmin)
admin.site.register(scheduleFile, scheduleFileAdmin)
admin.site.register(sequenceFile, sequenceFileAdmin)
admin.site.register(simbadType, simbadTypeAdmin)