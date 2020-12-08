import json
import requests
import boto3
import uuid
import my_settings


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.db.models import Q
from functools import reduce
from operator import __or__ as OR

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
            offset = 0
            limit = 5
            data = json.loads(request.body)
            employee_id = 1 #request.employee
            projects = Project.objects.prefetch_related("projectparticipant_set__employee").all()

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

                project_list = [{
                    'id' : project.id,
                    'title' : project.title,
                    'description' : project.description,
                    'start_date' : project.start_date.date(),
                    'end_date' : project.end_date.date(),
                    'is_private' : project.is_private,
                    'participants': len([par.employee for par in project.projectparticipant_set.all()])
                } for project in projects][offset:offset+limit]

                return JsonResponse({'main_list' : project_list}, status=200)

#                생성된 정보만 반환
#                add_project = {'id' : new_project.id,
#                            'created_by' : new_project.created_by.id,
#                            'title' : new_project.title,
#                            'description' : new_project.description,
#                            'is_private' : new_project.is_private,
#                            'start_date' : new_project.start_date,
#                            'end_date' : new_project.end_date,
#                            'participants' : participants.employee_id
#                           }

#                return JsonResponse({'add_project' : add_project}, status=201)

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

            project_list = [{
                'id' : project.id,
                'title' : project.title,
                'description' : project.description,
                'start_date' : project.start_date.date(),
                'end_date' : project.end_date.date(),
                'is_private' : project.is_private,
                'participants': len([par.employee for par in project.projectparticipant_set.all()])
            } for project in projects][offset:offset+limit]

            return JsonResponse({'main_list' : project_list}, status=200)

#            생성된 정보만 반환
#            add_project = {'id' : new_project.id,
#                           'created_by' : new_project.created_by.id,
#                           'title' : new_project.title,
#                           'description' : new_project.description,
#                           'start_date' : new_project.start_date,
#                           'end_date' : new_project.end_date,
#                           'is_private' : new_project.is_private,
#                           'participants' : participants.employee_id
#                          }
#
#            return JsonResponse({'add_project' : add_project}, status = 201)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e :
            return JsonResponse({'MESSAGE': f'VALUE_ERROR:{e}'}, status=400)

    def get(self,request):
        employee_id = 1 #request.employee
        limit = 7
        projects = Project.objects.prefetch_related("projectparticipant_set__employee").all()

        total_project = len(Project.objects.all())

        queries = dict(request.GET)

        if queries.get('offset'):
            offset = int(queries['offset'][0])
        else :
            offset = 0

        if offset > total_project:
            return JsonResponse({'MESSAGE' : 'OFFSET_OUT_OF_RANGE'}, status=400)

        print(queries.get('search'))

        if queries.get('search'):
            conditions = []
            search_list = queries.get('search')[0].split(' ')
            for word in search_list:
                conditions.append(Q(title__icontains = word))
                conditions.append(Q(description__icontains = word))
            projects = Project.objects.prefetch_related("projectparticipant_set__employee").all().filter(reduce(OR, conditions))


        else :
            projects = Project.objects.prefetch_related("projectparticipant_set__employee").all()

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
#            likes = ProjectLike.objects.filter(employee_id = employee_id)
#            like_list = [like_project.project_id for like_project in likes]

            likes = ProjectLike.objects.filter(employee_id = employee_id).select_related('project','employee').all()

            like_list = [{'id' : like.project.id,
                          'title' : like.project.title,
                          'description' : like.project.description,
                          'is_private' : like.project.is_private,
                          'start_date' : like.project.start_date,
                          'end_date' : like.project.end_date,
                          'participants' : len([par.employee_id for par in like.project.projectparticipant_set.all()])} for like in likes]

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

                    patch_list = [{'id' : project.id,
                                   'title' : project.title,
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

                patch_list = [{'id' : project.id,
                               'title' : project.title,
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
        employee_id = 1 #request.employee.id
        likes = ProjectLike.objects.filter(employee_id = employee_id).select_related('project','employee').all()

        like_list = [{'id' : like.project.id,
                      'title' : like.project.title,
                      'description' : like.project.description,
                      'is_private' : like.project.is_private,
                      'start_date' : like.project.start_date,
                      'end_date' : like.project.end_date,
                      'participants' : len([par.employee_id for par in like.project.projectparticipant_set.all()])} for like in likes]

        if ProjectLike.objects.filter(project_id=project_id, employee_id=employee_id).exists():
            project = ProjectLike.objects.get(employee_id = employee_id, project_id = project_id)
            project.delete()
            return JsonResponse({'like_list': like_list}, status=200)
        else:
            ProjectLike.objects.create(project_id=project_id, employee_id=employee_id)
            return JsonResponse({'like_list': like_list}, status=201)


    #@signin_decorator
    def get(self,request):
        employee_id = 1 #request.employee.id

        if ProjectLike.objects.filter(employee_id = employee_id).exists() :
#            likes = ProjectLike.objects.filter(employee_id = employee_id)
#            like_list = [like_project.project_id for like_project in likes]

            likes = ProjectLike.objects.filter(employee_id = employee_id).select_related('project','employee').all()

            like_list = [{'id' : like.project.id,
                          'title' : like.project.title,
                          'description' : like.project.description,
                          'is_private' : like.project.is_private,
                          'start_date' : like.project.start_date,
                          'end_date' : like.project.end_date,
                          'participants' : len([par.employee_id for par in like.project.projectparticipant_set.all()])} for like in likes]

            return JsonResponse({'like_list' : like_list}, status=200)
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
                    filecode = str(uuid.uuid1()).replace('-','')
                    filename = file.name
                    print(file)
                    print(file.name)
                    print(filename)
                    filesize = file.size

                    self.s3_client.upload_fileobj(
                        file,
                        "thisisninasbucket",
                        filename,
                        ExtraArgs={
                            "ContentType": file.content_type
                        }
                    )

                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    #file_name = file_name
                    attachment_list.append({'filename':filename,'filecode':filecode,'filesize':filesize,'fileurl':file_url})

            new_thread = ProjectDetail.objects.create(
                writer_id = Employee.objects.get(id=employee_id).id,
                content = request.POST['content'],
                project_detail_id = project_id
            )

            for file in attachment_list:
                new_projectattachment = ProjectAttachment.objects.create(
                    project_detail = ProjectDetail.objects.get(id = new_thread.id),
                    name = file['filename'],
                    url   = file['fileurl'],
                    size  = file['filesize'],
                    code  = file['filecode']
                )

            return JsonResponse({
                'project_thread': {
                    'thread_id':new_thread.project_detail_id,
                    'writer_id':new_thread.writer_id,
                    'writer_name':Employee.objects.get(id=employee_id).name_kor,
                    'content':new_thread.content,
                    'created_at':new_thread.created_at.date()},
                'attachments':[{
                    'id': attachment.id,
                    'code' : attachment.code,
                    'name' : attachment.name,
                    'url' : attachment.url,
                    'size' : attachment.size}for attachment in ProjectAttachment.objects.filter(project_detail_id = new_thread.id)]
                }, status=201)
        return JsonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status = 403)


    def get(self,request,project_id):
        employee_id = 1 #request.employee.id

        if ProjectParticipant.objects.filter(employee_id = employee_id, project_id = project_id).exists():

            project_details = ProjectDetail.objects.filter(project_detail_id = project_id).all().prefetch_related('projectattachment_set','projectreview_set')


            #project_details = ProjectDetail.objects.filter(project_detail_id = project_id).all().prefetch_related('projectattachment_set','projectreview_set')

            project_title = Project.objects.get(id=project_id).title

            detail_list4 = [{'thread_id' : detail.id,
                             'writer_id' : detail.writer_id,
                             'writer_name' : detail.writer.name_kor,
                             'content' : detail.content,
                              'attachment' : [{'id' : attachment.id,
                                               'name' : attachment.name,
                                               'url' : attachment.url,
                                               'size' : attachment.size} for attachment in detail.projectattachment_set.all()],
                             'comment_count' : len([com.content for com in detail.projectreview_set.all()]),
                             'comment' : [{'comment_id' :com.id,
                                           'writer_id' : com.writer.id,
                                           'writer_name' : com.writer.name_kor,
                                           'created_at' : com.created_at,
                                           'content' : com.content,
                                           } for com in detail.projectreview_set.all()]
                             } for detail in project_details]


#            detail_list3 = [[{'thread_id' : detail.id,
#                             'writer' : detail.writer_id,
#                             'content' : detail.content,
#                              'attachment' : {'id' : [attachment.id for attachment in detail.projectattachment_set.all()],
#                                              'name' : [attachment.name for attachment in detail.projectattachment_set.all()]}
#                              'attachment_id' : [attachment.id for attachment in detail.projectattachment_set.all()],
#                              'attachment_name' : [attachment.name for attachment in detail.projectattachment_set.all()],
#                              'commnet_writer_id' : [com.writer_id.name_kor for com in detail.projectreview_set.all()],
#                              'comment_created_at' : [com.created_at for com in detail.projectreview_set.all()]
#                             } for detail in project_details]]
#                            [[{'comment_writer_id' : com.writer_id.name_kor,
#                               'comment_created_at' : com.created_at,
#                               'comment_content' : com.content,
#                               'comment_count' : len(com.content)
#                              }for com in detail.projectreview_set.all()] for detail in project_details]]
#
#            detail_list2 = [[{'thread_id' : detail.id,
#                             'writer' : detail.writer_id,
#                             'content' : detail.content, 
#                             } for detail in project_details],
#                            [[{'thread_id' : par.project_detail_id,
#                               'attachment_id' : par.id,
#                               'attachment_name' : par.name
#                              } for par in detail.projectattachment_set.all()] for detail in project_details],
#                            [[{'comment_writer_id' : com.writer_id.name_kor,
#                               'comment_created_at' : com.created_at,
#                               'comment_content' : com.content,
#                               'comment_count' : len(com.content)
#                              }for com in detail.projectreview_set.all()] for detail in project_details]]



#                             'comment' : detail.projectreview_set.get().content,
#                             'comment_count' : len(detail.projectreview_set.content)
#                            } for detail in project_details.projectattachment_set.all().projectreview_set.all()]

#            detail_list = [[{'thread_id' : detail.id,
#                             'writer' : detail.writer_id,
#                             'content' : detail.content,
#                             'attachment_id' : par.id,
#                             'attachment_name' : par.name
#                            } for par in detail.projectattachment_set.all()]for detail in project_details]

#        detail_list = [[{'thread_id' : detail.id,
#                       'writer' : detail.writer_id,
#                       'content' : detail.content} for detail in project_details],
#                       [[{'attachment_id' : par.id,
#                        'attachment_name' : par.name,
#                          'thread_id' : detail.id} for par in detail.projectattachment_set.all()]for detail in project_details]]

        #추후 댓글들리스트도 추가해야함(해당 thread마다 댓글count도 필요)

            return JsonResponse({'project_title' : project_title,
                                 'detail_list' : detail_list4}, status=200)
        return JsonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status = 403)


    def patch(self,request,project_id,thread_id):
        employee_id = 1 #request.employee.id
        employee_auth = Employee.objects.get(id = employee_id).auth.id

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
                        'thread_id':new_trhead,
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

    def patch(self, request, notice_id):
        try:
            data = eval(request.POST['data'])
            # employee_id   = request.employee.id
            # employee_auth = request.employee.auth
            employee_id = 2
            employee_auth = Employee.objects.get(id = employee_id).auth.id

            target_notice = Notice.objects.filter(id = notice_id).values()[0]

            if target_notice['author_id'] != employee_id and employee_auth != 1:
                return JsonResponse({"message": "ACCESS_DENIED"},status=403)

            if 'deleting_files' in data:
                for file in data['deleting_files']:
                    if file in [f.id for f in target_notice.noticeattachment_set.all()]:
                        NoticeAttachment.objects.filter(id = file).delete()

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
            
            for file_url in attachment_list:
                NoticeAttachment.objects.create(
                    notice = target_notice.id,
                    file   = file_url
                )

            notice_field_list = [field.name for field in Notice._meta.get_fields()]

            for key in data.keys():
                if key in notice_field_list:
                    target_notice.update(**{key : data[key]})

            return JsonResponse(
                {
                'notice': {
                    'title':target_notice['title'],
                    'content':target_notice['content'],
                    'created_at':target_notice['created_at']
                },
                'attachments': [attach.file for attach in NoticeAttachment.objects.filter(notice_id = target_notice['id'])]+ attachment_list
                }, 
                status=200)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)


    #@jwt_utils.signin_decorator
    def delete(self,request,project_id,thread_id):
        employee_id   = 1 #request.employee.id
        #employee_auth = request.employee.auth

        thread = ProjectDetail.objects.get(id = thread_id)
        thread_comment = ProjectReview.objects.filter(project_detail_id = thread_id)

        if thread.writer_id != employee_id and employee_auth != 1:
            return JsonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status=403)

        thread.delete()
        thread_comment.delete()
        return JsonResponse({'MESSAGE' : 'DELETED'},status=200)


class CommentView(View):
    def post(self,request,project_id,thread_id):
        data = json.loads(request.body)
        employee_id = 1 #request.employee.id

        if not data['content'] :
            return JsonResponse({'MESSAGE' : 'NEED_CONTENT'}, status=404)

        if ProjectParticipant.objects.filter(employee_id = employee_id, project_id = project_id).exists():
            ProjectReview.objects.create(
                content = data['content'],
                project_detail_id = ProjectDetail.objects.get(id=thread_id).id,
                writer_id = employee_id
            )
            #전체 데이터 반환(새로 생긴 댓글, 댓글 count까지)

            return JsonResponse({'MESSAGE' : 'CREATE_SUCCESS'},status=201)
        return JSonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status = 403)

    def patch(self,request,project_id,thread_id,comment_id):
        data = json.loads(request.body)
        employee_id = 1 #request.employee.id
        comment = ProjectReview.objects.get(id=comment_id)

        if comment.writer_id == employee_id :
            ProjectReview.objects.update(
                content = data['content']
            )

            return JsonResponse({'MESSAGE' : 'PATCH_SUCCESS'},status = 200)
        return JsonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status = 403)

    def delete(self,request,project_id,thread_id,comment_id):
        employee_id = 1 #request.employee.id
        employee_auth = 1 #request.employee.auth
        comment = ProjectReview.objects.get(id=comment_id)

        if comment.writer_id != employee_id or employee_auth != 1 :
            return JsonResponse({'MESSAGE' : 'ACCESS_DENIED'}, status=403)

        comment.delete()
        return JsonResponse({'MESSAGE' : 'DELETE_SUCCESS'}, status = 200)




