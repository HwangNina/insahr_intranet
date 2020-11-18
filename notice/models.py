from django.db          import models
from django.utils       import timezone

from employee.models    import Employee

# Create your models here.

class Notice(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    author = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta():
        db_table = 'notices'


class NoticeAttachment(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    file = models.FileField(upload_to='file/%Y/%m/%d')

    class Meta():
        db_table = 'notice_attachments'
