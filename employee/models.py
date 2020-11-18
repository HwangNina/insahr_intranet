from django.db import models

# Create your models here.
class Auth(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return name

    class Meta():
        db_table = 'auths'


class Employee(models.Model):
    auth             = models.ForeignKey(Auth, on_delete=models.CASCADE)
    account          = models.CharField(max_length=50)
    password         = models.CharField(max_length=1000)
    name_kor         = models.CharField(max_length=50)
    name_eng         = models.CharField(max_length=50)
    nickname         = models.CharField(max_length=50)
    rrn              = models.CharField(max_length=1000, null=True)
    mobile           = models.CharField(max_length=50)
    emergency_num    = models.CharField(max_length=50)
    company_email    = models.EmailField(max_length=254)
    personal_email   = models.EmailField(max_length=254)
    bank_name        = models.CharField(max_length=50, null=True)
    bank_account     = models.CharField(max_length=1000, null=True)
    passport_num     = models.CharField(max_length=1000, null=True)
    address          = models.CharField(max_length=200, null=True)
    detailed_address = models.CharField(max_length=200, null=True)

    def __str__(self):
        return name_kor
    
    class Meta():
        db_table = 'employees'

class EmployeeDetail(models.Model):
    employee         = models.OneToOneField(employee, on_delete=models.CASCADE)
    joined_at        = models.DateField(auto_now=False, auto_now_add=False, null=True)
    probation_period = models.CharField(max_length=50, null=True)
    worked_since     = models.DateField(auto_now=False, auto_now_add=False, null=True)
    total_experience = models.CharField(max_length=50, null=True)
    annual_vacation  = models.IntegerField(null=True)
    annual_vacation_permission = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    status           = models.CharField(max_length=50, null=True)
    promotion_date   = models.DateField(auto_now=False, auto_now_add=False, null=True)
    promoted_at      = models.DateField(auto_now=False, auto_now_add=False, null=True)
    pass_num         = models.CharField(max_length=50, null=True)
    etc              = models.TextField(null=True)
    
    class Meta():
        db_table = 'employee_details'