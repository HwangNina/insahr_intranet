import os
import json
import bcrypt
import re
import jwt
import my_settings
import encrypt_utils
import jwt_utils
import requests

from django.views    import View
from employee.models import Auth, Employee, EmployeeDetail
from django.http     import JsonResponse

# Create your views here.

class SignUpView(View):

    def post(self, request):
        try:
            data  = json.loads(request.body)

            email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

            if (not (re.search(email_regex, data['company_email'])) or 
                not (re.search(email_regex, data['personal_email']))):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if Employee.objects.filter(account=data['account']).exists():
                return JsonResponse({"message": "ACCOUNT_EXISTS"}, status=400)

            # password encryption
            password       = data['password'].encode('utf-8')
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

            # rrn, bank account, passport number encryption
            def encryption(user_input):
                return encrypt_utils.encrypt(data[user_input], my_settings.SECRET.get('random'))

            encryption_needed = ['rrn', 'bank_account', 'passport_num']

            for idx in range(0, len(encryption_needed)):
                if encryption_needed[idx] in data:
                    encryption_needed[idx] = encryption(encryption_needed[idx]).decode('utf-8')
                else:
                    encryption_needed[idx] = ""

            # insert record
            Employee(
                auth             = Auth.objects.get(id = 5),
                account          = data['account'],
                password         = password_crypt,
                name_kor         = data['name_kor'],
                name_eng         = data['name_eng'],
                nickname         = data['nickname'],
                rrn              = encryption_needed[0],
                mobile           = data['mobile'],
                emergency_num    = data['emergency_num'],
                company_email    = data['company_email'],
                personal_email   = data['personal_email'],
                bank_name        = data['bank_name'],
                bank_account     = encryption_needed[1],
                passport_num     = encryption_needed[2],
                address          = data['address'],
                detailed_address = data['detailed_address'],
            ).save()

            EmployeeDetail(
                employee = Employee.objects.get(account = data['account'])
            ).save()
            
            return JsonResponse({"message": "SIGNUP_SUCCESS"}, status=200)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)


class SignInView(View):

    def post(self, request):
        try:
            data     = json.loads(request.body)

            # check id
            employee = Employee.objects.get(account=data['account'])

            # check password & token
            if bcrypt.checkpw(data['password'].encode('UTF-8'), employee.password.encode('UTF-8')):
                key       = my_settings.SECRET.get('SECRET_KEY')
                algorithm = my_settings.SECRET.get('JWT_ALGORITHM')
                token     = jwt.encode({'employee' : employee.id},key, algorithm = algorithm).decode('UTF-8')
                return JsonResponse({"token": token, "message": "SIGNIN_SUCCESS", "name" : employee.name}, status=200)

            else:
                return JsonResponse({"message": "INVALID_PASSWORD"}, status=401)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)

        except Employee.DoesNotExist:
            return JsonResponse({"message": "INVALID_USER"}, status=401)


class EmployeeInfoView(View):
    @jwt_utils.signin_decorator    
    def get(self, request):
        employee_id     = request.employee.id
        target_employee = Employee.objects.filter(id = employee_id).values()[0]

        def decryption(info):
            return encrypt_utils.decrypt(
                          target_employee[info], my_settings.SECRET.get('random')
                          ).decode('utf-8')
        
        decryption_needed = ['rrn', 'bank_account', 'passport_num']

        for idx in range(0, len(decryption_needed)):
            if target_employee[decryption_needed[idx]]:
                decryption_needed[idx] = decryption(decryption_needed[idx])
            else:
                decryption_needed[idx] = ""

        return JsonResponse(
            {
                'account'           : target_employee['account'],
                'name_kor'          : target_employee['name_kor'],
                'name_eng'          : target_employee['name_eng'],
                'nickname'          : target_employee['nickname'],
                'rrn'               : decryption_needed[0],
                'mobile'            : target_employee['mobile'],
                'emergency_num'     : target_employee['emergency_num'],
                'company_email'     : target_employee['company_email'],
                'personal_email'    : target_employee['personal_email'],
                'bank_name'         : target_employee['bank_name'],
                'bank_account'      : decryption_needed[1],
                'passport_num'      : decryption_needed[2],
                'address'           : target_employee['address'],
                'detailed_address'  : target_employee['detailed_address'] 
            }
        )

    @jwt_utils.signin_decorator
    def patch(self, request):
        try:
            data     = json.loads(request.body)
            employee_id = request.employee.id

            target_employee = Employee.objects.get(id = employee_id)

            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if (company_email in data and not (re.search(regex, data['company_email']))
                or personal_email in data and not (re.search(regex, data['personal_email']))):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if bcrypt.checkpw(data['password'].encode('UTF-8'), target_employee.password.encode('UTF-8')):
                if 'new_password' in data:
                    new_password       = data['new_password'].encode('utf-8')
                    new_password_crypt = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
                    
                    target_employee.password = new_password

                employee_field_list = [field.name for field in Employee._meta.get_fields()]
                employee_field_list.remove('password')

                for field in employee_field_list:
                    if field in data:
                        if field == (rrn or bank_account or passport_num):
                            target_employee.update(**{field : encrypt_utils.encrypt(data[field], my_settings.SECRET.get('random'))})
                        else:
                            target_employee.update(**{field : data[field]})

                target_employee.save()

                return JsonResponse({"message": "MODIFICATION_SUCCESS"}, status=200)

            else:
                return JsonResponse({'message': "WRONG_PASSWORD"}, status=400)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)


# only admin can access
class EmployeeManagementView(View):
    @jwt_utils.signin_decorator 
    def get(self, request, employee_id):
        admin_id = request.employee.id

        if Employee.objects.get(id = admin_id).auth != 1:
            return JsonResponse(
                {"message": "NO_AUTHORIZATION"},
                status=403
            )

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
                decryption_needed[idx] = ""

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
            'admin_auth':{
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
                    if field == (rrn or bank_account or passport_num):
                        target_employee.update(**{field : encrypt_utils.encrypt(data[field], my_settings.SECRET.get('random'))})
                    else:
                        target_employee.update(**{field : data[field]})

            for field in employee_detail_field_list:
                if field in data:
                    target_employee.update(**{field : data[field]})
            return JsonResponse({"message": "MODIFICATION_SUCCESS"}, status=200)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)