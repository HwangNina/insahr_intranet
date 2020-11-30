import json
import requests

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from project.models import (
    Project,
    ProjectLike,
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
    def get(self,request):
        recent_projects = list(Project.objects.all())[-4:] 
        employee_id = 1 #request.employee

        project_list = [{
            'id' : project.id,
            'title' : project.title,
            'description' : project.description,
            'start_date' : project.start_date.date(),
            'end_date' : project.end_date.date(),
            'is_private' : project.is_private,
            'participants': len([par.employee for par in project.projectparticipant_set.all()])
        } for project in recent_projects]

        if ProjectLike.objects.filter(employee_id = employee_id).exists() :
            likes = ProjectLike.objects.filter(employee_id = employee_id)
            like_list = [like_project.project_id for like_project in likes]

            return JsonResponse({'main_list' : project_list, 'like_project_list' : like_list}, status=200)

        return JsonResponse({'main_list' : project_list}, status=200)

class PeopleView(View):
    def get(self,request):
        try:
            people = Employee.objects.all()
            people_list = [{
                'id' : person.id,
                'name' : person.name_kor
            } for person in people]

            return JsonResponse({'people_list' : people_list}, status=200)

        except Exception as e:
            return JsonResponse({'MESSAGE' : f"EXCEPT_ERROR:{e}"}, status=400)

class ProjectListView(View):
    #@signin_decorator

    def post(self,request):
        try:
            data = json.loads(request.body)
            employee_id = 1 #request.employee

            #person = employee_id값, 1은True = 비공개 프로젝트, 0은 False = 공개
            if data['is_private'] == 0 :
                employees = Employee.objects.all()
                new_project = Project.objects.create(
                    created_by = Employee.objects.get(id=employee_id),
                    title = data['title'],
                    description = data['description'],
                    is_private = data['is_private'],
                    start_date = data['start_date'],
                    end_date = data['end_date']
                )

                for people in employees :
                    ProjectParticipant.objects.create(
                        employee = Employee.objects.get(id=people.id),
                        project = Project.objects.get(id=new_project.id)
                    )
                return JsonResponse({'MESSAGE' : 'CREATE_SUCCESS'}, status=201)

            if len(data['participant']) == 0 :
                return JsonResponse({'MESSAGE' : 'at_least_one_participant_needed'}, status=400)
            new_project = Project.objects.create(
                created_by = Employee.objects.get(id=employee_id),
                title = data['title'],
                description = data['description'],
                is_private = data['is_private'],
                start_date = data['start_date'],
                end_date = data['end_date']
            )

            for person in data['participant']:
                ProjectParticipant.objects.create(
                    employee = Employee.objects.get(id=person),
                    project = Project.objects.get(id=new_project.id)
                )
            return JsonResponse({'MESSAGE' : 'CREATE_SUCCESS'}, status=201)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e :
            return JsonResponse({'MESSAGE': f'VALUE_ERROR:{e}'}, status=400)

    def get(self,request):
        projects = Project.objects.prefetch_related("projectparticipant_set__employee").all()
        employee_id = 1 #request.employee

        project_list = [{
            'id' : project.id,
            'title' : project.title,
            'description' : project.description,
            'start_date' : project.start_date.date(),
            'end_date' : project.end_date.date(),
            'is_private' : project.is_private,
            'participants': len([par.employee for par in project.projectparticipant_set.all()])
        } for project in projects]

        if ProjectLike.objects.filter(employee_id = employee_id).exists() :
            likes = ProjectLike.objects.filter(employee_id = employee_id)
            like_list = [like_project.project_id for like_project in likes]
            return JsonResponse({'main_list' : project_list, 'like_project_list' : like_list}, status=200)

        return JsonResponse({'main_list' : project_list}, status=200)

    def delete(self,request,project_id):
        data = json.loads(request.body)
        employee_id = 1 #request.employee
        post = get_object_or_404(Project, pk=project_id)

        if post.created_by.id == int(employee_id) :
            participants = ProjectParticipant.objects.filter(project = project_id)
            participants.delete()
            post.delete()
            return JsonResponse({'MESSAGE' : 'DELETE_SUCCESS'}, status=200)

    def patch(self,request,project_id):
        try:
            data = json.loads(request.body)
            employee_id = 1 #request.employee
            post = Project.objects.filter(id = project_id)
            #project_id는 하나이니까 filter아니고 get
            participants = ProjectParticipant.objects.filter(project_id = project_id)

            if post.first().created_by_id == int(employee_id) :
                if data['is_private'] == 0 :
                    employees = Employee.objects.all()
                    post.update(
                        title = data['title'],
                        description = data['description'],
                        is_private = data['is_private'],
                        start_date = data['start_date'],
                        end_date = data['end_date']
                    )

                    participants = ProjectParticipant.objects.filter(project = project_id)
                    participants.delete()

                    for people in employees :
                        ProjectParticipant.objects.create(
                            employee = Employee.objects.get(id=people.id),
                            project = Project.objects.get(id=post.first().id)
                        )
                    return JsonResponse({'MESSAGE' : 'UPDATE_SUCCESS'}, status=201)

                if len(data['participant']) == 0 :
                    return JsonResponse({'MESSAGE' : 'at_least_one_participant_needed'}, status=400)

                post.update( 
                    title = data['title'],
                    description = data['description'],
                    is_private = data['is_private'],
                    start_date = data['start_date'],
                    end_date = data['end_date']
                )

                participants = ProjectParticipant.objects.filter(project = project_id)
                participants.delete()

                for person in data['participant']:
                    ProjectParticipant.objects.create(
                        employee = Employee.objects.get(id=person),
                        project = Project.objects.get(id=post.first().id)
                    )
                return JsonResponse({'MESSAGE' : 'UPDATE_SUCCESS'}, status=201)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e :
            return JsonResponse({'MESSAGE': f'VALUE_ERROR:{e}'}, status=400)

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
 




