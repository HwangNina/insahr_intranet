from django.db import models

from employee.models import Employee

# Create your models here.

class EmployeeDetail(models.Model):
    employee         = models.OneToOneField(Employee, on_delete=models.CASCADE)
    joined_at        = models.DateField(auto_now=False, auto_now_add=False, null=True)
    probation_period = models.CharField(max_length=50, null=True)
    worked_since     = models.DateField(auto_now=False, auto_now_add=False, null=True)
    total_experience = models.CharField(max_length=50, null=True)
    annual_vacation  = models.IntegerField(null=True)
    annual_vacation_permission = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL, related_name='employee')
    status           = models.CharField(max_length=50, null=True)
    promotion_date   = models.DateField(auto_now=False, auto_now_add=False, null=True)
    promoted_at      = models.DateField(auto_now=False, auto_now_add=False, null=True)
    pass_num         = models.CharField(max_length=50, null=True)
    etc              = models.TextField(null=True)
    
    class Meta():
        db_table = 'employee_details'
