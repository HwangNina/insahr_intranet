import json
import boto3
import datetime
import uuid

from django.views import View
from django.http import JsonResponse

from notice.models import Notice, NoticeAttachment

class NoticeListView(View):

    def get(self, request):
        try:
            data = json.loads(request.body)
            limit = 5
            if data['offset']:
                offset = int(data['offset'][0])
            else:
                offset = 0

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
                'no': notice.id,
                'title': notice.title,
                'date': notice.created_at
                } for notice in notice_page_list
            ]

            return JsonResponse(
                {
                    "notices":returning_list
                },
                status=200
                )

        except ValueError:
            return JsonResponse(
                {
                    "message": "VALUE_ERROR"
                },
                status=400
            )        


class NoticeDetailView(View):

    def post(self, request):
        try:
            employee_id = request.employee.id
            data = request.POST
        
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
                        }
                    )
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url = None

            new_notice = Notice.objects.create(
                        title     = data['title'],
                        content   = data['content'],
                        author    = employee_id,
                        )

            for file in attachment_list:
                NoticeAttachment.objects.create(
                    notice = new_notice.id,
                    file   = file_url
                )
            
            return JsonResponse(
                {
                'notice': new_notice.values(),
                'attachments': attachment_list
                }, 
                status=201)

        except KeyError:
            return JsonResponse(
                {
                'message':'KEY_ERROR'
                }, 
                status=400)
    
    def get(self, request, notice_id):
        target_notice       = Notice.objects.get(id = notice_id).select_related('notice_attachment_file')
        target_notice_idx   = Notice.objects.all().values().index(target_notice)

        previous_notice     = Notice.objects.all().values()[target_notice_idx-1]
        next_notice         = Notice.objects.all().values()[target_notice_idx+1]

        return JsonResponse(
            {
                "notice":{
                    "title": target_notice.title,
                    "author": target_notice.author,
                    "created_at":target_notice.created_at,
                    "content": target_notice.content,
                    "attachments":[f for f in target_notice.notice_attachment.file]
                },
                "previous":{
                    "title": previous_notice.title,
                    "created_at": previous_notice.created_at
                },
                "next":{
                    "title": next_notice.title,
                    "created_at": next_notice.created_at
                }
            },status=200
        )        

    def patch(self, request, notice_id):
        try:
            employee_id   = request.employee.id
            target_notice = Notice.objects.get(id = notice_id)
            data          = request.POST

            NoticeAttachment.objects.filter(notice_id = target_notice.id).delete()

            if target_notice.author != employee_id:
                return JsonResponse(
                    {
                        "message": "ACCESS_DENIED"
                    },
                    status=403
                )

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
                        }
                    )
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url = None
            
            for file in attachment_list:
                NoticeAttachment.objects.create(
                    notice = new_notice.id,
                    file   = file_url
                )

            if data['title']:
                target_notice.title = data['title']
            if data['content']:
                target_notice.content = data['content']

            return JsonResponse(
                {
                'notice': target_notice.values(),
                'attachments': attachment_list
                }, 
                status=201)

        except KeyError:
            return JsonResponse(
                {
                'message':'KEY_ERROR'
                }, 
                status=400)
    
    def delete(self, request, notice_id):
        employee_id   = request.employee.id
        target_notice = Notice.objects.get(id = notice_id)
       
        if target_notice.author != employee_id:
            return JsonResponse(
                {
                    "message": "ACCESS_DENIED"
                },
                status=403
            )
        
        target_notice.delete()

        return JsonResponse(
            {
                "message":"DELETED"
            },
            status=200
        )