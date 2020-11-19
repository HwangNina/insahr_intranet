import json
import requests

from django.http import JsonResponse
from django.views import View

from project.models import (
    Project,
    PrivateProject,
    ProjectDetail,
    ProjectReview,
    ProjectParticipant,
    ProjectAttachment
)

from employee.models import (
    Auth,
    Employee,
    EmployeeDetail,
)

from .jwt_utils import signin_decorator

#class MainListView(View):
#    @signin_decorator
#    def get(self, request) :
#        employee_id = request.employee
#
#        projects = Project.objects.all()
#
#        if pr
#        persons = PrivateProject.objects.
#
#        projects_list = [{
#            'id' : project.id,
#            'title' : project.title,
#            'description' : project.description
#        } for project in projects]
#


            'persons' : project.private_project_set.count




