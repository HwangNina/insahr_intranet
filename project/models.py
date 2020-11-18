from django.db import models


class Project(models.Model):
    title = models.CharField(max_length = 45)
    is_private = models.BooleanField(default = False)

    class Meta :
        db_table = 'projects'

class PrivateProject(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete = models.CASCADE, null = True)
    project = models.ForeignKey('Project', on_delete = models.CASCADE, null = True)

    class Meta :
        db_table = 'private_projects'

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
    is_liked = models.BooleanField(default = False)

    class Meta :
        db_table = 'project_participants'

class ProjectAttachment(models.Model):
    project_detail = models.ForeignKey('ProjectDetail', on_delete = models.CASCADE)
    name = models.CharField(max_length = 100)

    class Meta :
        db_table = 'project_attachments'

