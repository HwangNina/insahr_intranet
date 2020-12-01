import os
import json
import bcrypt
import re
import jwt
import my_settings
import encrypt_utils
import jwt_utils
import requests

from django.http     import JsonResponse
from django.views    import View

from employee.models import Auth, Employee
from hr_mgmt.models import EmployeeDetail

# Create your views here.
class HumanResourceListView(View):
    @jwt_utils.signin_decorator 
    def get(self, request):
        try:
            admin_id = request.employee.id
            admin_auth = request.employee.auth

            limit = 6

            queries = dict(request.GET)

            if queries.get('offset'):
                offset = int(queries['offset'][0])
            else:
                offset = 0

            if admin_auth != 1:
                return JsonResponse(
                    {"message": "NO_AUTHORIZATION"},
                    status=403
                )

            if queries.get('search'):
                conditions = []
                search_list = queries.get('search')[0].split(' ')
                for name in search_list:
                    conditions.append(Q(name_kor__icontains = name))
                employee_list = Employee.objects.filter(reduce(OR, conditions))
            else: 
                employee_list = Employee.objects.all()

            if offset > len(employee_list):
                return JsonRespose(
                    {'message':'OFFSET_OUT_OF_RANGE'},status=400)
            
            hr_mgmt_page_list = [hr for hr in employee_list][offset:offset+limit]

            returning_list = [
                {
                    'no':hr_mgmt_page_list.index(hr),
                    'name':hr.name_kor,
                    'nickname':hr.nickname,
                    'mobile':hr.mobile,
                    'dob':hr.rrn[:7],
                    'email':hr.company_email,
                    'joined_at':hr.joined_at
                } for hr in hr_mgmt_page_list
            ]
            return JsonResponse({"employees":returning_list}, status=200)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)         

class HumanResourceManagementView(View):
    @jwt_utils.signin_decorator 
    def get(self, request, employee_id):
        admin_id = request.employee.id
        admin_auth = request.employee.auth

        if admin_auth != 1:
            return JsonResponse({"message": "NO_AUTHORIZATION"},status=403)

        target_employee = Employee.objects.prefetch_related('employeedetail_set').filter(id = employee_id).values()[0]
        target_employee_detail = target_employee.employeedetail_set.all()[0]

        def decryption(info):
            return encrypt_utils.decrypt(
                          target_employee[info], my_settings.SECRET.get('random')
                          ).decode('utf-8')
        
        decryption_needed = ['rrn', 'bank_account', 'passport_num']

        for idx in range(0, len(decryption_needed)):
            if target_employee[decryption_needed[idx]]:
                decryption_needed[idx] = decryption(decryption_needed[idx])
            else:
                decryption_needed[idx] = None

        return JsonResponse(
            {'all_auth':{
                'account'          : target_employee['account'],
                'name_kor'         : target_employee['name_kor'],
                'name_eng'         : target_employee['name_eng'],
                'nickname'         : target_employee['nickname'],
                'rrn'              : decryption_needed[0],
                'mobile'           : target_employee['mobile'],
                'emergency_num'    : target_employee['emergency_num'],
                'company_email'    : target_employee['company_email'],
                'personal_email'   : target_employee['personal_email'],
                'bank_name'        : target_employee['bank_name'],
                'bank_account'     : decryption_needed[1],
                'passport_num'     : decryption_needed[2],
                'address'          : target_employee['address'],
                'detailed_address' : target_employee['detailed_address'] 
                },
            'admin_only':{
                'auth'             : target_employdd['auth']
                'joined_at'        : target_employee_detail.joined_at,
                'probation_period' : target_employee_detail.probation_period,
                'worked_since'     : target_employee_detail.worked_since,
                'total_experience' : target_employee_detail.total_experience,
                'annual_vacation'  : target_employee_detail.annual_vacation,
                'annual_vacation_permission' : target_employee_detail.annual_vacation_permission,
                'status'           : target_employee_detail.status,
                'promotion_date'   : target_employee_detail.promotion_date,
                'promoted_at'      : target_employee_detail.promoted_at,
                'pass_num'         : target_employee_detail.pass_num,
                'etc'              : target_employee_detail.etc
                }
            }
        )

    @jwt_utils.signin_decorator 
    def patch(self, request, employee_id):
        try:
            admin_id = request.employee.id
            data = json.loads(request.body)

            if Employee.objects.get(id = admin_id).auth != 1:
                return JsonResponse(
                    {"message": "NO_AUTHORIZATION"},
                    status=403
                )

            target_employee = Employee.objects.prefetch_related('employeedetail_set').filter(id = employee_id).values()[0]
            target_employee_detail = target_employee.employeedetail_set.all()[0]

            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if (company_email in data and not (re.search(regex, data['company_email']))
                or personal_email in data and not (re.search(regex, data['personal_email']))):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)


            employee_field_list = [field.name for field in Employee._meta.get_fields()]
            employee_field_list.remove('password')
            employee_detail_field_list = [field.name for field in EmployeeDetail._meta.get_fields()]
            
            for field in employee_field_list:
                    if field in data:
                        if field in ['rrn', 'bank_account', 'passport_num']:
                            Employee.objects.filter(id = employee_id).update(**{field : encrypt_utils.encrypt(data[field], my_settings.SECRET.get('random')).decode('utf-8')})
                        else:
                            Employee.objects.filter(id = employee_id).update(**{field : data[field]})

            for field in employee_detail_field_list:
                if field in data:
                    target_employee.update(**{field : data[field]})
            return JsonResponse({"message": "MODIFICATION_SUCCESS"}, status=200)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)