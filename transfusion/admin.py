from django.contrib import admin

# Register your models here.
from transfusion.models import TeacherProfile, Course, Assignment, Link, File

admin.site.register(TeacherProfile)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Link)
admin.site.register(File)