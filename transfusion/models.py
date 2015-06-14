from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


class TeacherProfile(models.Model):
    user = models.OneToOneField(User)
    school = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()


class Course(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True, max_length=500)

    def __str__(self):
        return self.name + " (" + self.user.get_full_name() + ")"


class Assignment(models.Model):
    course = models.ForeignKey(Course)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()

    def __str__(self):
        return self.name + " (" + self.course.name + ")"

    @property
    def is_past_due(self):
        if timezone.now().date() >= self.due_date:
            return True
        return False


class Link(models.Model):
    course = models.ForeignKey(Course)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return self.name + " (" + self.course.name + ")"


class File(models.Model):
    course = models.ForeignKey(Course)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    filename = models.TextField()
    path = models.TextField()

    def __str__(self):
        return self.name + " (" + self.course.name + ")"