from django.contrib import admin
from .models import observation,scheduleMaster,scheduleDetail,sequenceFile,scheduleFile

class observationAdmin(admin.ModelAdmin):
    list_display = ("targetId","observationDate")

class scheduleMasterAdmin(admin.ModelAdmin):
    list_display = ("userId","schedule_date")
    
class scheduleDetailAdmin(admin.ModelAdmin):
    list_display = ("scheduleDetailId","targetId")
    
class sequenceFileAdmin(admin.ModelAdmin):
    list_display = ("sequenceFileId","sequenceFileName")
    
class scheduleFileAdmin(admin.ModelAdmin):
    list_display = ("scheduleFileId","scheduleFileName")

admin.site.register(sequenceFile, sequenceFileAdmin)
admin.site.register(scheduleMaster, scheduleMasterAdmin) 
admin.site.register(scheduleDetail, scheduleDetailAdmin)
admin.site.register(scheduleFile, scheduleFileAdmin)
admin.site.register(observation, observationAdmin)