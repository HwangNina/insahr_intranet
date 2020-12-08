import json
import datetime
import jwt_utils

from django.views import View
from django.http import JsonResponse

from employee.models import Auth, Employee
from attendance.models import AttendanceLabel, Attendance

class WorkTimeView(View):
    #@jwt_utils.signin_decorator
    def post(self,request):
        try:
            data = json.loads(request.body)
            #employee_id = request.employee.id

            if data['start_time'] :
                Attendance.objects.create(
                    employee = Employee.objects.get(id = employee_id),
                    label = AttendanceLabel.objects.get(id = 1),
                    begin_at = data['start_time']
                )
                return JsonResponse({'MESSAGE' : 'START_TIME_SAVED'}, status=21)

            if data['totla_pause'] and data['start_time']:
                Attendance.objects.create(
                    total_pause = data['total_pause']


class WorkingHourView(View):
    # @jwt_utils.signin_decorator
    def post(self, request):
        try:
            data = json.loads(request.body)
            # employee_id = request.employee.id

            new_attendance = Attendance(
                employee = Employee.objects.get(id = data['employee']),
                label = AttendanceLabel.objects.get(id = data['label']),
                begin_at = data['start_time'],
                written_by = Employee.objects.get(id = employee_id),
                amended_by = Employee.objects.get(id = employee_id),
                content = data['content']
            ).save()

#            new_attendance = Attendance(
#                employee = Employee.objects.get(id = data['employee']),
#                label = AttendanceLabel.objects.get(id = data['label']),
#                begin_at = data['begin_at'],
#                written_by = Employee.objects.get(id = employee_id),
#                amended_by = Employee.objects.get(id = employee_id),
#                content = data['content']
#            ).save()


            return JsonResponse({"message":new_attendance},status=200)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)

    def get(self, request):
        working_hour_list = list(Attendance.objects.filter((
            Q(begin_at__year = data['year']) & Q(begin_at__month = data['month'])) | ((
            Q(finish_at__year = data['year']) & Q(finish_at__month = data['month'])))
            ).order_by('begin_at'))

        return JsonResponse(
            {
                "working_hours":[
                    {"employee":data.employee,
                    "label":data.label,
                    "begin_at":data.begin_at,
                    "finish_at":data.finish_at,
                    "written_by":data.written_by,
                    "amended_by":data.amended_by,
                    "content":data.content,
                    "total_working_hour":data.finish_at - data.begin_at - data.total_pause} 
                    if data.finish_at 
                    else {"employee":data.employee,
                    "label":data.label,
                    "begin_at":data.begin_at,
                    "written_by":data.written_by,
                    "amended_by":data.amended_by,
                    "content":data.content} 
                    for data in working_hour_list
                ]
            },status=200
        )


