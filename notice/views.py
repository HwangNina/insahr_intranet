import json
import boto3
import datetime
import uuid

from django.views import View
from django.http import JsonResponse

from notice.models import Notice, NoticeAttachment
from notice.forms import NoticeAttachmentForm

class NoticeView(View):

    def post(self, request):
        try:
            user_id=request.user.id
            content=request.POST['content']
        
            if request.FILES.get('attachment'):
                attachment_list = []
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
                    file_url=f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url=None

            new_notice = Notice.objects.create(
                'title' = data['title'],
                'content' = data['content'],
                'author' = user_id,
            )

            for file in attachment_list:
                NoticeAttachment.objects.create(
                    'notice' = new_notice.id,
                    'file' = file_url
                )
            
            return JsonResponse({
                'notice': new_notice.values(),
                'attachments': attachment_list
                }, status=200)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
