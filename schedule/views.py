import json
import boto3
import jwt_utils
import uuid
import my_settings
from django.conf import settings

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q
from datetime         import datetime
from django.utils     import timezone

from schedule.models import (
    Label, 
    Schedule, 
    ScheduleParticipant, 
    ScheduleAttachment
    )
from employee.models import Auth, Employee

# Create your views here.

class ScheduleListView(View):
    @jwt_utils.signin_decorator
    def get(self, request):
        data  = json.loads(request.body)

        schedule_list = list(Schedule.objects.filter((
            Q(begin_at__year = data['year']) & Q(begin_at__month = data['month'])) or (
            Q(finish_at__year = data['year']) & Q(finish_at__month = data['month']))
            )).order_by('begin_at')
    
        returning_list = [{
            "begin_at":schedule.begin_at,
            "finish_at":schedule.finish_at,
            "label":schedule.label,
            "title":schedule.title,
        } for schedule in schedule_list]

        return JsonResponse(
            {
                "schedule": returning_list
            },
            status=200
        )


class ScheduleDetailView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    @jwt_utils.signin_decorator
    def post(self, request):
        try:
            data = eval(request.POST['data'])
            employee_id = request.employee.id

            if len(data['participants']) == 0:
                participant_list = Employee.objects.all().values()
            else:
                participant_list = data['participants']

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
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/schedule/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url = None

            created_by = Employee.objects.get(id = employee_id)

            new_schedule = Schedule.objects.create(
                label       = Label.objects.get(id = data['label']),
                title       = data['title'],
                location    = data['location'],
                begin_at    = timezone.make_aware(datetime.strptime(data['begin_at'], '%Y-%m-%d %H:%M:%S')),
                finish_at   = timezone.make_aware(datetime.strptime(data['finish_at'], '%Y-%m-%d %H:%M:%S')),
                description = data['description'],
                written_by  = created_by,
                amended_by  = created_by,
            )

            for file in attachment_list:
                ScheduleAttachment.objects.create(
                    schedule = Schedule.objects.get(id = new_schedule.id),
                    file     = file_url
                )

            for participant in participant_list:
                ScheduleParticipant.objects.create(
                    schedule = Schedule.objects.get(id = new_schedule.id),
                    employee = Employee.objects.get(id = participant)
                )

            return JsonResponse({"message":"POST_SUCCESS"}, status=201)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)

    # @jwt_utils.signin_decorator
    def get(self, request, schedule_id):
        target_schedule = Schedule.objects.select_related('label'
                          ).prefetch_related('scheduleparticipant_set__employee','scheduleattachment_set'
                          ).get(id = schedule_id)

        return JsonResponse(
            {
                'schedule':{'label': target_schedule.label.name,
                'title': target_schedule.title,
                'location': target_schedule.location,
                'begin_at': target_schedule.begin_at,
                'finish_at': target_schedule.finish_at,
                'description': target_schedule.description,
                'written_by': str(target_schedule.written_by),
                'amended_by': str(target_schedule.amended_by),
                'craeted_at': target_schedule.created_at,
                'updated_at': target_schedule.updated_at},
                'participants': [participant.employee.name_kor for participant in target_schedule.scheduleparticipant_set.all()],
                'attachments':[{'id':f.id, 'file':f.file} for f in target_schedule.scheduleattachment_set.all()]
            },
            status=200
        )
    
    @jwt_utils.signin_decorator
    def patch(self, request, schedule_id):
        try:
            data = eval(request.POST['data'])
            employee_id     = request.employee.id
            employee_auth   = request.employee.auth

            target_schedule = Schedule.objects.select_related('label').prefech_related('scheduleattachment_set').filter(id = schedule_id)

            if employee_id != target_schedule.values()[0]['written_by_id'] and employee_auth != 1:
                return JsonResponse({"message": "ACCESS_DENIED"},status=403)

            if 'deleting_files' in data:
                for file in data['deleting_files']:
                    if file in [f.id for f in target_schedule.scheduleattachement_set.all()]:
                        ScheduleAttachment.objects.filter(id = file).delete()

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
                    file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/schedule/{filename}"
                    attachment_list.append(file_url)
            else:
                file_url = None
            
            schedule_field_list = [field.name for field in Schedule._meta.get_fields()]

            for key in data.keys():
                if key in schedule_field_list:
                    target_schedule.update(**{key : data[key]})

            target_schedule.update(updated_at = datetime.datetime.now().strftime("%Y-%m-%d"))

            for file in attachment_list:
                NoticeAttachment.objects.create(
                    notice = Notice.objects.get(id = target_schedule['id']),
                    file   = file_url
                )

            return JsonResponse({'message':'MODIFICATION_SUCCESS'}, status=200)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

    @jwt_utils.signin_decorator
    def delete(self, request, schedule_id):
        employee_id   = request.employee.id
        employee_auth = request.employee.auth

        target_schedule = Schedule.objects.get(id = schedule_id)
        target_schedule_attachment = ScheduleAttachment.objects.filter(schedule_id = schedule_id)

        if employee_id != target_schedule.written_by.id and employee_auth != 1:
            return JsonResponse({"message": "ACCESS_DENIED"},status=403)
        
        target_schedule.delete()
        target_schedule_attachment.delete()

        return JsonResponse({"message":"DELETED"},status=200)
