from django.db import models

from employee.models import Employee

# Create your models here.
class AttendanceLabel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta():
        db_table = 'attendance_labels'


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    label = models.OneToOneField(AttendanceLabel, on_delete=models.CASCADE)
    begin_at = models.DateTimeField(auto_now=False, auto_now_add=False)
    finish_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    total_pause = models.DurationField(null=True)
    written_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amended_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    content = models.TextField(null=True)

    def __str__(self):
        return self.name

    class Meta():
        db_table = 'attendances'
