import json

from django.views import View
from django.http import JsonResponse

from schedule.models import Label, Schedule, ScheduleParticipant, ScheduleAttachment, Date, ScheduleDate

# Create your views here.

class ScheduleView(View):

    def post(self, request):

        data  = json.loads(request.body)
        # employee_id   = request.employee.id
        employee_id = 1

        # Schedule(
        #     label = Label.objects.get(id = data['label']),
        #     title = data['title'],
        #     location = data['location'],
        #     date = data['date']

        # )

        