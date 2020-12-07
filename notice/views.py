import json
import boto3
import uuid
import datetime
import jwt_utils
import my_settings

from functools        import reduce
from operator         import __or__ as OR
from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q

from notice.models   import Notice, NoticeAttachment
from employee.models import Employee

class NoticeMainView(View):

    def get(self, request):
        recent_three = list(Notice.objects.all().values())[-3:]

        returning_object = [{'title': notice['title'],
                            'content':notice['content'],
                            'date':notice['created_at']} for notice in recent_three[::-1]]

        return JsonResponse(
            {"returning_notices" : returning_object}, status=200)
            

class NoticeListView(View):

    def get(self, request):
        try:
            limit = 5
            total_notice = len(Notice.objects.all())

            queries = dict(request.GET)

            if queries.get('offset'):
                offset = int(queries['offset'][0])
            else:
                offset = 0

            if offset > total_notice:
                return JsonResponse(
                    {'message':'OFFSET_OUT_OF_RANGE'},status=400)
                    
            if queries.get('search'):
                conditions = []
                search_list = queries.get('search')[0].split(' ')
                for word in search_list:
                    conditions.append(Q(title__icontains = word))
                notice_list = Notice.objects.filter(reduce(OR, conditions))
            else:
                notice_list = Notice.objects.all()


            notice_page_list = [{
                'no': notice.id,
                'title': notice.title,
                'date': notice.created_at
            } for notice in notice_list][::-1][offset:offset+limit]

            return JsonResponse({"notices":notice_page_list,"total_notices":len(notice_list)}, status=200)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)   


class NoticeDetailView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=my_settings.AWS_ACCESS_KEY['MY_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=my_settings.AWS_ACCESS_KEY['MY_AWS_SECRET_ACCESS_KEY']
    )
    # @jwt_utils.signin_decorator
    def post(self, request):
        try:
            # employee_id = request.employee.id
            employee_id = 2

            attachment_list = []
            if request.FILES.getlist('attachment', None):
                for f in request.FILES.getlist('attachment'): 
                    filename = str(uuid.uuid1()).replace('-','')
                    self.s3_client.upload_fileobj(
                        f,
                        "thisisninasbucket",
                        filename,
                        ExtraArgs={
                            "ContentType": f.content_type
                        }
                    )
                    print(f)
                    print(filename)
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url = None
    
            new_notice = Notice.objects.create(
                        title = request.POST['title'],
                        content = request.POST['content'],
                        author    = Employee.objects.get(id = employee_id),
                        )

            for file_url in attachment_list:
                NoticeAttachment.objects.create(
                    notice = Notice.objects.get(id = new_notice.id),
                    file   = file_url
                )
            
            return JsonResponse(
                {
                'notice': {
                    'title':new_notice.title,
                    'content':new_notice.content,
                    'created_at':new_notice.created_at
                },
                'attachments':[{'id':f.id, 'file':f.file} for f in NoticeAttachment.objects.filter(notice_id=new_notice.id)]
                }, 
                status=201)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

    def get(self, request, notice_id):
        target_notice = dict(Notice.objects.filter(id = notice_id).values()[0])

        notice_list       = [notice for notice in Notice.objects.all().values()]
        target_notice_idx = notice_list.index(target_notice)

        if target_notice_idx > 1:
            previous_notice    = notice_list[target_notice_idx-1]
            returning_previous = {
                    "title": previous_notice['title'],
                    "created_at": previous_notice['created_at']
                }
        else:
            returning_previous = {}

        if target_notice_idx < len(notice_list)-1:
            next_notice    = notice_list[target_notice_idx+1]
            returning_next = {
                    "title": next_notice['title'],
                    "created_at": next_notice['created_at']
                }
        else:
            returning_next = {}
        
        return JsonResponse(
            {
                "notice":{
                    "title": target_notice['title'],
                    "created_at":target_notice['created_at'],
                    "content": target_notice['content'],
                    "attachments":[f['file'] for f in NoticeAttachment.objects.filter(notice_id = target_notice['id']).values()]
                },
                "previous":returning_previous,
                "next":returning_next
            },
            status=200
        )        

    # @jwt_utils.signin_decorator
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
    
    @jwt_utils.signin_decorator
    def delete(self, request, notice_id):
        employee_id = request.employee.id
        employee_auth = request.employee.auth.id
        target_notice = Notice.objects.get(id = notice_id)
       
        if target_notice.author.id != employee_id and employee_auth != 1:
            return JsonResponse({"message": "ACCESS_DENIED"},status=403)
        
        target_notice.delete()

        return JsonResponse({"message":"DELETED"},status=200)
        
