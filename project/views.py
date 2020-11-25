import json
import requests

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from project.models import (
    Project,
    ProjectDetail,
    ProjectReview,
    ProjectParticipant,
    ProjectAttachment
)

from employee.models import (
    Auth,
    Employee,
    # EmployeeDetail,
)

from jwt_utils import signin_decorator

class MainListView(View):
    #@signin_decorator
    def get(self, request):
        recent_projects = list(Project.objects.all().values())[-4:]
        employee_id = 1 #request.employee

        project_list = [{
            'id' : project['id'],
            'title' : project['title'],
            'description' : project['description'],
            'start_date' : project['start_date'].date(),
            'end_date' : project['end_date'].date(),
            'is_private' : project['is_private'],
            'is_liked' : project['is_liked']
        } for project in recent_projects]

#        likes = ProjectParticipant.objects.filter(employee_id = employee_id)
#        like_list = [{
#            'project_id' : like.project_id,
#            'is_liked' : like.is_liked
#        }for like in likes]
        #[like.is_liked for like in likes]
        return JsonResponse({'main_list' : project_list}, status=200)

class ProjectListView(View):
    #@signin_decorator
    def post(self,request):
        data = json.loads(request.body)
        employee_id = 1 #request.employee

        Project.objects.create(
            employee = employee_id,
            title = data['title'],
            description = data['description'],
            is_private = data['is_private'],
            start_date = data['start_data'],
            end_date = data['end_date']
        )
        return JsonResponse({'MESSAGE' : 'CREATE_SUCCESS'}, status=201)

    def get(self,request):
        projects = Project.objects.all()
        employee_id = 1 #request.employee

        project_list = [{
            'id' : project.id,
            'title' : project.title,
            'description' : project.description,
            'start_date' : project.start_date.date(),
            'end_date' : project.end_date.date(),
            'is_private' : project.is_private,
            'is_liked' : project.is_liked,
            'participants': len([par.employee for par in project.projectparticipant_set.all()])
        } for project in projects]

        return JsonResponse({'main_list' : project_list}, status=200)

    def delete(self,request,project_id):
        data = json.loads(request.body)
        employee_id = request.employee
        post = get_object_or_404(Project, pk=project_id)

        if post.employee_id == int(employee_id) :
            post.delete()
            return JsonResponse({'MESSAGE' : 'DELETE_SUCCESS'}, status=200)

    def patch(self,request,project_id):
        data = json.loads(request.body)
        employee_id = request.employee
        post = Project.objects.filter(id == data['id'])

        if post.employee_id == int(employee_id) :
            post.update(
                title = data['title'],
                description = data['description'],
                is_private = data['is_private'],
                start_date = data['start_data'],
                end_date = data['end_date']
            )
            return JsonResponse({'MESSAGE' : 'UPDATE_SUCCESS'}, status = 200)

class ThreadView(View):
    def post(self,request,project_id):
        data = json.loads(request.body)
        employee_id = request.employee
        employee_name = Employee.objects.get(id = employee_id).name

        if ProjectParticipants.objects.filter(employee_id = employee_id).exists() :
            ProjectDetail.objects.create(
                writer = employee_name,
                content = data['content'],
                project_detail = project_id
            )
            # 첨부파일 저장 내용 추가해야함 
            return JsonResponse({'MESSAGE' : 'CREATE_SUCCESS'}, status=201)
        return JsonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status = 400)


# 첨부파일 저장 
#        if request.FILES.get('attachment'):
#            attachment_list = []
#            attachments     = request.FILES['attachment']
#
#            for file in attachments:
#                filename = str(uuid.uuid1()).replace('-','')
#
#                self.s3_client.upload_fileobj(
#                    attachment,
#                    "insahr_notice_attachment",
#                    filename,
#                    ExtraArgs={
#                        "ContentType": file.content_type
#                    })
#
#                file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
#
#                attachment_list.append(file_url)
#
#        else:
#            file_url = None
#            ProjectDetail.objects.create(
#                writer = employee_id,
#                content = data['content'],
#                project_detail = project_id
#            )
#
#            for file in attachment_list:
#                NoticeAttachment.objects.create(
#                    notice = new_notice.id,
#                    file   = file_url
#                )
#
        return JsonResponse({'MESSAGE' : 'CREATE_SUCCESS'}, status=201)
#
#    def get(self, request, project_id) :
#        employee_id = request.employee
#
#        project_title = Project.objects.get(id = project_id)
#        name = Employee.objects.get(id = employee_id).name_kor
#        projects_list = [{
#            'id' : project.id,
#            'title' : project.title,
#        } for project in projects]
#
 




