import json
import boto3
import datetime
import uuid

from django.views import View
from django.http import JsonResponse

from notice.models import Notice, NoticeAttachment
from employee.models import Employee

class NoticeListView(View):
    
    def get(self, request, **search):
        try:
            limit = 5
            offset = int(request.GET.get('offset', 0))

            if search:
                notice_list = Notice.objects.filter(title__icontains = search['search']).values()
            else:
                notice_list = Notice.objects.all().values()

            if offset > len(notice_list):
                return JsonResponse(
                    {
                    'message':'OFFSET_OUT_OF_RANGE'
                    },
                    status=400)
            
            notice_page_list = [notice for notice in notice_list][offset:offset+limit]

            returning_list = [
                {
                'no': notice['id'],
                'title': notice['title'],
                'date': notice['created_at']
                } for notice in notice_page_list
            ]

            return JsonResponse({"notices":returning_list}, status=200)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)   


class NoticeDetailView(View):

    def post(self, request):
        try:
            employee_id = request.employee.id
            data        = json.loads(request.body)
        
            attachment_list = []
            if request.FILES.get('attachment', None):
                attachments = request.FILES['attachment']

                for file in attachments:
                    filename = str(uuid.uuid1()).replace('-','')
                
                    self.s3_client.upload_fileobj(
                        attachment,
                        "insahr_notice_attachment",
                        filename,
                        ExtraArgs={
                            "ContentType": file.content_type
                        }
                    )
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url = None
    
            new_notice = Notice.objects.create(
                        title     = data['title'],
                        content   = data['content'],
                        author    = Employee.objects.get(id = employee_id),
                        )

            for file in attachment_list:
                NoticeAttachment.objects.create(
                    notice = new_notice.id,
                    file   = file_url
                )
            
            return JsonResponse(
                {
                'notice': {
                    'title':new_notice.title,
                    'content':new_notice.content,
                    'created_at':new_notice.created_at
                },
                'attachments': attachment_list
                }, 
                status=201)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)
    
    def get(self, request, notice_id):
        target_notice       = dict(Notice.objects.filter(id = notice_id).values()[0])

        notice_list         = [notice for notice in Notice.objects.all().values()]
        target_notice_idx   = notice_list.index(target_notice)

        if target_notice_idx > 1:
            previous_notice    = notice_list[target_notice_idx-1]
            returning_previous = {
                    "title": previous_notice['title'],
                    "created_at": previous_notice['created_at']
                }
        else:
            returning_previous = {}

        if target_notice_idx < len(notice_list):
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
                    "attachments":[f.file for f in NoticeAttachment.objects.filter(notice_id = target_notice['id']).values()]
                },
                "previous":returning_previous,
                "next":returning_next
            },
            status=200
        )        

    @jwt_utils.signin_decorator
    def patch(self, request, notice_id):
        try:
            employee_id   = request.employee.id
            employee_auth = request.employee.auth

            target_notice = Notice.objects.get(id = notice_id)
            data          = json.loads(request.body)

            NoticeAttachment.objects.filter(notice_id = target_notice.id).delete()

            if target_notice.author.id != employee_id or employee_auth != 1:
                return JsonResponse({"message": "ACCESS_DENIED"},status=403)

            attachment_list = []
            if request.FILES.get('attachment'):
                attachments = request.FILES['attachment']

                for file in attachments:
                    filename = str(uuid.uuid1()).replace('-','')
                    self.s3_client.upload_fileobj(
                        attachment,
                        "insahr_notice_attachment",
                        filename,
                        ExtraArgs={
                            "ContentType": file.content_type
                        }
                    )
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    attachment_list.append(file_url)

            else:
                file_url = None
            
            for file in attachment_list:
                NoticeAttachment.objects.create(
                    notice = target_notice.id,
                    file   = file_url
                )

            if 'title' in data:
                target_notice.title = data['title']

            if 'content' in data:
                target_notice.content = data['content']

            target_notice.save()

            return JsonResponse(
                {
                'notice': {
                    'title':target_notice.title,
                    'content':target_notice.content,
                    'created_at':target_notice.created_at
                },
                'attachments': attachment_list
                }, 
                status=201)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)
    
    @jwt_utils.signin_decorator
    def delete(self, request, notice_id):
        employee_id   = request.employee.id
        employee_id = 1
        target_notice = Notice.objects.get(id = notice_id)
       
        if target_notice.author.id != employee_id or employee_auth != 1:
            return JsonResponse({"message": "ACCESS_DENIED"},status=403)
        
        target_notice.delete()

        return JsonResponse({"message":"DELETED"},status=200)