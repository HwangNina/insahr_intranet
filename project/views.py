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

class MainListView(View):
    #@signin_decorator

    def post(self,request):
        data = json.loads(request.body)
        employee_id = request.employee

        Project.objects.create(
            employee = employee_id,
            title = data['title'],
            description = data['description'],
            is_private = data['is_private'],
            start_date = data['start_data'],
            end_date = data['end_date']
        )

        return JsonResponse({'MESSAGE' : 'CREATE_SUCCESS'}, status=201)


    def delete(self,request):
        data = json.loads(request.body)
        employee_id = request.employee

        if project.id == data['id'] and  project.employee == employee_id :
            Project.objects.delete(
            )

        return JsonResponse({'MESSAGE' : 'DELETE_SUCCESS'}, status=200)



        if request.FILES.get('attachment'):
            attachment_list = []
            attachments     = request.FILES['attachment']

            for file in attachments:
                filename = str(uuid.uuid1()).replace('-','')

                self.s3_client.upload_fileobj(
                    attachment,
                    "insahr_notice_attachment",
                    filename,
                    ExtraArgs={
                        "ContentType": file.content_type
                    })

                file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"

                attachment_list.append(file_url)

        else:
            file_url = None
            new_project = Project.objects.create(
                title     = data['title'],
                description   = data['description'],
                employee = employee_id,
            )

            for file in attachment_list:
                NoticeAttachment.objects.create(
                    notice = new_notice.id,
                    file   = file_url
                )

        return JsonResponse({
            'notice': new_notice.values(),
            'attachments': attachment_list
        }, status=201)

        except KeyError:
            return JsonResponse(
                {'message':'KEY_ERROR'}, status=400)







    def get(self, request) :
        employee_id = request.employee

        projects = Project.objects.all()


        persons = PrivateProject.objects.

        projects_list = [{
            'id' : project.id,
            'title' : project.title,
            'description' : project.description
        } for project in projects]



            'persons' : project.private_project_set.count




