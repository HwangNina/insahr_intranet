import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q

from schedule.models import Label, Schedule, ScheduleParticipant, ScheduleAttachment, Date, ScheduleDate

# Create your views here.

class ScheduleListView(View):
    @jwt_utils.signin_decorator
    def get(self, request):
        data  = json.loads(request.body)

        schedule_list = list(Schedule.objects.filter((Q(begin_at__year = data['year']) & Q(begin_at__month = data['month'])) or (Q(finish_at__year = data['year'] & finish_at__month = data['month']))).order_by('begin_at'))

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
    @jwt_utils.signin_decorator
    def post(self, request):
        try:
            data        = json.loads(request.body)
            employee_id = request.employee.id

            if len(data['participants']):
                participant_list = Employee.objects.all().values()
            else:
                participant_list = data['participants']

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

            new_schedule = Schedule.objects.create(
                label = Label.objects.get(id = data['label']),
                title = data['title'],
                location = data['location'],
                begin_at = data['begin_at'],
                finish_at = data['finish_at'],
                description = data['description'],
                written_by = Employee.objects.get(id = employee_id),
                amended_by = Employee.objects.get(id = employee_id),
            )

            for file in attachment_list:
                ScheduleAttachment.objects.create(
                    schedule = new_schedule.id,
                    file   = file_url
                )

            for participant in participant_list:
                ScheduleParticipant.objects.create(
                    schedule = new_schedule.id,
                    employee = participant.id
                )

            return JsonResponse({"message":"POST_SUCCESS"}, status=201)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)

    @jwt_utils.signin_decorator
    def get(self, request, schedule_id):
        target_schedule = Schedule.objects.select_related('label'
                          ).prefetch_related('scheduleparticipant_set_employee','scheduleattachment_set_file'
                          ).get(id = schedule_id)

        return JsonResponse(
            {
                'label': target_schedule.label.name,
                'title': target_schedule.title,
                'location': target_schedule.location.
                'begin_at': target_schedule.begin_at,
                'finish_at': target_schedule.finish_at,
                'description': target_schedule.description,
                'written_by': target_schedule.written_by,
                'amended_by': target_schedule.amended_by,
                'craeted_at': target_schedule.created_at,
                'updated_at': target_schedule.updated_at,
                'participant': [participant.name for participant in target_schedule.scheduleparticipant_set_employee.all()],
                "attachments":[f.file for f in ScheduleAttachment.objects.filter(schedule_id = target_schedule.id).values()]
            },
            status=200
        )
    
    @jwt_utils.signin_decorator
    def patch(self. request, schedule_id):
        try:
            employee_id     = request.employee.id
            employee_auth   = request.employee.auth
            target_schedule = Schedule.objects.select_related('label').filter(id = schedule_id).values()[0]
            data            = json.loads(request.body)

            if employee_id != target_schedule['written_by'].id or employee_auth != 1:
                return JsonResponse({"message": "ACCESS_DENIED"},status=403)

            ScheduleAttachment.objects.filter(schedule_id = target_schedule.id).delete()

            if target_schedule.author.id != employee_id:
                return JsonResponse({'message':'ACCESS_DENIED'}, status=403)

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

            schedule_field_list = [field.name for field in Schedule._meta.get_fields()]

            for key in data.keys():
                if key in schedule_field_list:
                    target_schedule[key] = data[key]

            target_schedule['updated_at'] = timezone.now()

            target_schedule.save()

            return JsonResponse({'message':'MODIFICATION_SUCCESS'}, status=200)

        except KeyError as e :
            return JsonResponse({'MESSAGE': f'KEY_ERROR:{e}'}, status=400)

    @jwt_utils.signin_decorator
    def delete(self, request, schedule_id):
        employee_id   = request.employee.id
        employee_auth = request.employee.auth

        target_schedule = Schedule.objects.get(id = schedule_id)

        if employee_id != target_schedule.written_by.id or employee_auth != 1:
            return JsonResponse({"message": "ACCESS_DENIED"},status=403)
        
        target_schedule.delete()

        return JsonResponse({"message":"DELETED"},status=200)
