from django.contrib import admin
from .models import observation,scheduleMaster,scheduleDetail,sequenceFile,fitsFile

class observationAdmin(admin.ModelAdmin):
    list_display = ("targetId","observationDate")

class scheduleMasterAdmin(admin.ModelAdmin):
    list_display = ("userId","schedule_date")
    
class scheduleDetailAdmin(admin.ModelAdmin):
    list_display = ("scheduleDetailId","targetId")
     
class fitsFileAdmin(admin.ModelAdmin):
    list_display = ("fitsFileId","fitsFileName","fitsFileDate")

admin.site.register(scheduleMaster, scheduleMasterAdmin) 
admin.site.register(scheduleDetail, scheduleDetailAdmin)
admin.site.register(observation, observationAdmin)
admin.site.register(fitsFile, fitsFileAdmin)
