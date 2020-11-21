from django.db import models

from employee.models import Employee

# Create your models here.
class Label(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta():
        db_table = 'labels'


class Schedule(models.Model):
    label       = models.ForeignKey(Label, on_delete=models.DO_NOTHING)
    title       = models.CharField(max_length=500)
    location    = models.CharField(max_length=200)
    time        = models.TimeField(auto_now=False, auto_now_add=False)
    description = models.TextField()
    written_by  = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name='schedule_wrote_employee')
    amended_by  = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name='schedule_amended_employee')
    created_at  = models.DateField(auto_now=True, auto_now_add=False)
    updated_at  = models.DateField(auto_now=False, auto_now_add=True)
    participant = models.ManyToManyField(Employee, through = 'ScheduleParticipant', related_name='schedule_employee')
    date        = models.ManyToManyField("Date", through = 'ScheduleDate')

    def __str__(self):
        return self.title
    
    class Meta():
        db_table = 'schedules'


class ScheduleParticipant(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    class Meta():
        db_table = 'schedule_participants'


class ScheduleAttachment(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    file = models.CharField(max_length=500)

    class Meta():
        db_table = 'schedule_attachments'


class Date(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)

    class Meta():
        db_table = 'dates'


class ScheduleDate(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.ForeignKey(Date, on_delete=models.CASCADE)

    class Meta():
        db_table = 'schedule_dates'