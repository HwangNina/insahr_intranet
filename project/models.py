from django.db import models
from django.utils import timezone

class Project(models.Model):
    title = models.CharField(max_length = 45)
    description = models.CharField(max_length = 100,null=True)
    is_private = models.BooleanField(default = False)
    start_date = models.DateTimeField(auto_now=False, auto_now_add=False, default = timezone.now )
    end_date = models.DateTimeField(auto_now=False, auto_now_add=False, default = timezone.now)
    created_by = models.ForeignKey('employee.Employee', on_delete = models.CASCADE, default ='')
 
    class Meta :
        db_table = 'projects'

class ProjectDetail(models.Model):
    writer = models.ForeignKey('employee.Employee', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    content = models.TextField()
    project_detail = models.ForeignKey('Project', on_delete = models.CASCADE)

    class Meta :
        db_table = 'project_details'

class ProjectReview(models.Model):
    writer = models.ForeignKey('employee.Employee', on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add = True)
    content = models.TextField()
    project_detail = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE)

    class Meta :
        db_table = 'project_reviews'

class ProjectParticipant(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete = models.CASCADE)
    project = models.ForeignKey('Project', on_delete = models.CASCADE)

    class Meta :
        db_table = 'project_participants'

class ProjectAttachment(models.Model):
    project_detail = models.ForeignKey('ProjectDetail', on_delete = models.CASCADE)
    url = models.CharField(max_length = 500)
    name = models.CharField(max_length = 100)
    size = models.IntegerField()

    class Meta :
        db_table = 'project_attachments'

class ProjectLike(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete = models.CASCADE)
    project = models.ForeignKey('project.Project', on_delete = models.CASCADE)

    class Meta :
        db_table = 'project_likes'

