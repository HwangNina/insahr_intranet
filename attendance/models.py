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
    label = models.ForeignKey(AttendanceLabel, on_delete=models.CASCADE)
    begin_at = models.IntegerField()
    finish_at = models.IntegerField(null=True)
    total_pause = models.DurationField(default='0 00:00:00')
    written_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name = 'written_by')
    amended_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name = 'amended_by')
    content = models.TextField(null=True)

    def __str__(self):
        return self.name

    class Meta():
        db_table = 'attendances'
