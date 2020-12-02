import json
import requests
import boto3
import uuid
import my_settings


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
                    participants = ProjectParticipant.objects.create(
                        employee = Employee.objects.get(id=people.id),
                        project = Project.objects.get(id=new_project.id)
                    )

                add_project = {'id' : new_project.id,
                            'created_by' : new_project.created_by.id,
                            'title' : new_project.title,
                            'description' : new_project.description,
                            'is_private' : new_project.is_private,
                            'start_date' : new_project.start_date,
                            'end_date' : new_project.end_date,
                            'participants' : participants.employee_id
                           }

                return JsonResponse({'add_project' : add_project}, status=201)

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
                participants = ProjectParticipant.objects.create(
                    employee = Employee.objects.get(id=person),
                    project = Project.objects.get(id=new_project.id)
                )

                add_project = {'id' : new_project.id,
                        'created_by' : new_project.created_by.id,
                        'title' : new_project.title,
                        'description' : new_project.description,
                        'start_date' : new_project.start_date,
                        'end_date' : new_project.end_date,
                        'is_private' : new_project.is_private,
                        'participants' : participants.employee_id
                       }

            return JsonResponse({'add_project' : add_project}, status = 201)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e :
            return JsonResponse({'MESSAGE': f'VALUE_ERROR:{e}'}, status=400)

    def get(self,request):
        offset = int(request.GET.get("offset", "0"))
        limit = int(request.GET.get("limit", "5"))
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
        } for project in projects][offset:offset+limit]

        if ProjectLike.objects.filter(employee_id = employee_id).exists() :
            likes = ProjectLike.objects.filter(employee_id = employee_id)
            like_list = [like_project.project_id for like_project in likes]
            return JsonResponse({'main_list' : project_list, 'like_project_list' : like_list}, status=200)

        return JsonResponse({'main_list' : project_list}, status=200)

    #@signin_decorator
    def delete(self,request,project_id):
        data = json.loads(request.body)
        employee_id = 1 #request.employee
        post = get_object_or_404(Project, pk=project_id)

        if post.created_by.id == int(employee_id) :
            participants = ProjectParticipant.objects.filter(project = project_id)
            participants.delete()
            post.delete()

            return JsonResponse({'MESSAGE' : 'DELETE_SUCCESS'}, status=200)

    #@signin_decorator
    def patch(self,request,project_id):
        try:
            data = json.loads(request.body)
            employee_id = 1 #request.employee
            post = Project.objects.filter(id = project_id)
            participants = ProjectParticipant.objects.filter(project_id = project_id)

            if post.first().created_by.id == int(employee_id) :
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
                    participants.delete() # 프로젝트 참여자 삭제 후 생성해야함

                    for people in employees :
                        patch_participant = ProjectParticipant.objects.create(
                            employee = Employee.objects.get(id=people.id),
                            project = Project.objects.get(id=post.first().id)
                        )

                    patch_list = [{'title' : project.title,
                                   'description' : project.description,
                                   'is_private' : project.is_private,
                                   'start_date' : project.start_date,
                                   'end_date' : project.end_date,
                                   'participants' : patch_participant.employee_id} for project in post]

                    return JsonResponse({'patch_list' : patch_list}, status=200)

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
                    patch_participant = ProjectParticipant.objects.create(
                        employee = Employee.objects.get(id=person),
                        project = Project.objects.get(id=post.first().id)
                    )

                patch_list = [{'title' : project.title,
                               'description' : project.description,
                               'is_private' : project.is_private,
                               'start_date' : project.start_date,
                               'end_date' : project.end_date,
                               'participants' : patch_participant.employee_id} for project in post]

                return JsonResponse({'patch_list' : patch_list}, status=200)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e :
            return JsonResponse({'MESSAGE': f'VALUE_ERROR:{e}'}, status=400)


class LikeView(View):
    #@signin_decorator
    def post(self,request,project_id):
        try:
            data = json.loads(request.body)
            employee_id = 1 #request.employee.id
 
            if ProjectLike.objects.filter(project_id=project_id, employee_id=employee_id).exists():
                ProjectLike.objects.delete(employee = employee_id, project = project_id)
                #project.like.remove(user_id)
                return JsonResponse({'MESSAGE': 'PROJECT_IS_UNLIKED'}, status=200)
            else:
                ProjectLike.objects.create(project_id=project_id, employee_id=employee_id)
                #posting.like.add(user_id)
                return JsonResponse({'MESSAGE': 'PROJECT_IS_LIKED'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'MESSAGE':'JSON_ERROR'}, status=400)

    #@signin_decorator
    def get(self,request):
        employee_id = 1 #request.employee.id

        if ProjectLike.objects.filter(employee_id = employee_id).exists() :
            likes = ProjectLike.objects.filter(employee_id = employee_id)
            like_list = [like_project.project_id for like_project in likes]
            #id값만 리스트로 넘김. 프론트랑 맞춰보고 dict 형태 필요하면 변경하기
            return JsonResponse({'like_project_list' : like_list}, status=200)
        return JsonResponse({'MESSAGE' :'LIKELIST_DOES_NOT_EXIST'})


class ThreadView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=my_settings.AWS_ACCESS_KEY['MY_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=my_settings.AWS_ACCESS_KEY['MY_AWS_SECRET_ACCESS_KEY']
    )
    #@signin_decorator
    def post(self,request,project_id): 
        #data = request.POST['data']
        #data = eval(request.POST['data'])
        #data = json.loads(request.body)
        employee_id = 1 #request.employee.id
        #content = request.POST.get(['content'])

        if ProjectParticipant.objects.filter(employee_id = employee_id, project_id = project_id).exists():
            attachment_list = []
            if request.FILES.getlist('attachment', None):
                for file in request.FILES.getlist('attachment'):
                    filename = str(uuid.uuid1()).replace('-','')
                    self.s3_client.upload_fileobj(
                        file,
                        "thisisninasbucket",
                        filename,
                        ExtraArgs={
                            "ContentType": file.content_type
                        }
                    )
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url = None

            new_thread = ProjectDetail.objects.create(
                writer_id = Employee.objects.get(id=employee_id).id,
                content = request.POST['content'],
                project_detail_id = project_id
            )

            for file_url in attachment_list:
                new_projectattachment = ProjectAttachment.objects.create(
                    project_detail = ProjectDetail.objects.get(id = new_thread.id),
                    name   = file_url
                )

            return JsonResponse(
                {
                    'project_thread': {
                        'writer_id':new_thread.writer_id,
                        'writer_name':Employee.objects.get(id=employee_id).name_kor,
                        'content':new_thread.content,
                        'created_at':new_thread.created_at.date()
                    },
                    'attachments':{
                        'id':new_projectattachment.project_detail_id,
                        'file':new_projectattachment.name}
                }, status=201)
        return JsonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status = 400)

# 이렇게 하면 아예 빈리스트를 반환하는데 왜 인지 이유를 모르겠다...
#        'attachments':[{
#                        'id':file.project_detail_id,
#                        'file':file.name} for file in ProjectAttachment.objects.filter(project_detail_id=new_thread.project_detail_id)]
#                }, status=201)


    def get(self,request,project_id):
        employee_id = 1 #request.employee.id
        project_details = ProjectDetail.objects.filter(project_detail_id = project_id).values()
        project_title = Project.objects.get(id=project_id)

        detail_list = {[{'thread_id' : detail['id'],
                       'writer' : detail['writer_id'],
                       'content' : detail['content']} for detail in  project_details],
                       {
                           'attachment' : [{'id' : file.id,
                                           'name' : file.name}
                                           for file in ProjectAttachment.objects.filter(project_detail_id = detail['id'])]}}

        return JsonResponse({'detail_list' : detail_list}, status=200)



#    def get(self,request,project_id):
#        target_notice = dict(Notice.objects.filter(id = notice_id).values()[0])
#
#        notice_list       = [notice for notice in Notice.objects.all().values()]
#        target_notice_idx = notice_list.index(target_notice)
#
#        if target_notice_idx > 1:
#            previous_notice    = notice_list[target_notice_idx-1]
#            returning_previous = {
#                    "title": previous_notice['title'],
#                    "created_at": previous_notice['created_at']
#                }
#        else:
#            returning_previous = {}
#
#        if target_notice_idx < len(notice_list)-1:
#            next_notice    = notice_list[target_notice_idx+1]
#            returning_next = {
#                    "title": next_notice['title'],
#                    "created_at": next_notice['created_at']
#                }
#        else:
#            returning_next = {}
#
#        return JsonResponse(
#            {
#                "notice":{
#                    "title": target_notice['title'],
#                    "created_at":target_notice['created_at'],
#                    "content": target_notice['content'],
#                    "attachments":[f['file'] for f in NoticeAttachment.objects.filter(notice_id = target_notice['id']).values()]
#                },
#                "previous":returning_previous,
#                "next":returning_next
#            },
#            status=200
#        )







