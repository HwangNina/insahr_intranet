from django.db import models

# Create your models here.
class Auth(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta():
        db_table = 'auths'


class Employee(models.Model):
    auth             = models.ForeignKey(Auth, on_delete=models.CASCADE)
    # profile_image    = models.ImageField(_(""), upload_to=None, height_field=None, width_field=None, max_length=None)
    account          = models.CharField(max_length=50)
    password         = models.CharField(max_length=1000)
    name_kor         = models.CharField(max_length=50)
    name_eng         = models.CharField(max_length=50)
    nickname         = models.CharField(max_length=50, null=True)
    rrn              = models.CharField(max_length=1000)
    mobile           = models.CharField(max_length=50)
    emergency_num    = models.CharField(max_length=50, null=True)
    company_email    = models.EmailField(max_length=254, null=True)
    personal_email   = models.EmailField(max_length=254, null=True)
    bank_name        = models.CharField(max_length=50, null=True)
    bank_account     = models.CharField(max_length=1000, null=True)
    passport_num     = models.CharField(max_length=1000, null=True)
    post_num         = models.CharField(max_length=50, null=True)
    address          = models.CharField(max_length=200, null=True)
    detailed_address = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name_kor
    
    class Meta():
        db_table = 'employees'