import os
import json
import bcrypt
import re
import jwt
import my_settings
import encrypt_utils
import jwt_utils
import requests

from django.views           import View
from employee.models        import Auth, Employee, EmployeeDetail
from django.http            import JsonResponse


# Create your views here.

class SignUpView(View):

    def post(self, request):
        try:
            data  = json.loads(request.body)

            def encryption(user_input):
                return encrypt_utils.encrypt(data[user_input], my_settings.SECRET.get('raw'))

            email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

            if not (re.search(email_regex, data['company_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if not (re.search(email_regex, data['personal_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if Employee.objects.filter(account=data['account']).exists():
                return JsonResponse({"message": "ACCOUNT_EXISTS"}, status=400)

            password       = data['password'].encode('utf-8')
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

            encryption_needed = ['rrn', 'bank_account', 'passport_num']
            encryption_result = []

            for info in encryption_needed:
                if info in data:
                    encryption_result.append(encryption(info).decode('utf-8'))
                else:
                    encryption_result.append("")

            Employee(
                auth             = Auth.objects.get(id = data['auth']),
                account          = data['account'],
                password         = password_crypt,
                name_kor         = data['name_kor'],
                name_eng         = data['name_eng'],
                nickname         = data['nickname'],
                rrn              = encryption_result[0],
                mobile           = data['mobile'],
                emergency_num    = data['emergency_num'],
                company_email    = data['company_email'],
                personal_email   = data['personal_email'],
                bank_name        = data['bank_name'],
                bank_account     = encryption_result[1],
                passport_num     = encryption_result[2],
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
            data = json.loads(request.body)
            employee = Employee.objects.get(account=data['account'])

            # if bcrypt.checkpw(data['password'].encode('UTF-8'), employee.password.encode('UTF-8')):
            #     admin_key       = my_settings.SECRET.get('admin_secret')
            #     employee_key    = my_settings.SECRET.get('admin_secret')
            #     probition_key   = my_settings.SECRET.get('probition_secret')
            #     parttime_key    = my_settings.SECRET.get('parttime_secret')
            #     freelancer_key  = my_settings.SECRET.get('freelancer_secret')

            #     algorithm       = my_settings.SECRET.get('JWT_ALGORITHM')

            #     if employee.auth == 1:
            #         key = admin_key
            #     if employee.auth == 2:
            #         key = employee_key
            #     if employee.auth == 3:
            #         key = probition_key
            #     if employee.auth == 4:
            #         key = parttime_key
            #     if employee.auth == 5:
            #         key = freelancer_key

                # key = my_settings.SECRET.get('secret_key')

                # algorithm = my_settings.SECRET.get('JWT_ALGORITHM')

                # token     = jwt.encode({'employee' : employee.id},key, algorithm = algorithm).decode('UTF-8')
                # return JsonResponse({"token": token, "message": "SIGNIN_SUCCESS", "name" : employee.name}, status=200)

            # else:
            #     return JsonResponse({"message": "INVALID_PASSWORD"}, status=401)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"message": "INVALID_USER"}, status=401)


class EmployeeInfoView(View):
    
    def get(self, request):
        data            = json.loads(request.body)
        target_employee = Employee.objects.get(id = data['employee'])
        target_employee_detail = EmployeeDetail.objects.get(id = target_employee.id)

        if target_employee.rrn:
            rrn_decrypt          = encrypt_utils.decrypt(
                                   target_employee.rrn, my_settings.SECRET.get('raw')
                                   ).decode('utf-8')
        else:
            rrn_decrypt = ""

        if target_employee.bank_account:
            bank_account_decrypt = encrypt_utils.decrypt(
                                    target_employee.bank_account, my_settings.SECRET.get('raw')
                                    ).decode('utf-8')
        else:
            bank_account_decrypt = ""

        if target_employee.passport_num:
            passport_num_decrypt = encrypt_utils.decrypt(
                                   target_employee.passport_num, my_settings.SECRET.get('raw')
                                   ).decode('utf-8')
        else:
            passport_num_decrypt = ""

        # if employee_auth == 1:

            # return JsonResponse(
            #     {'all_auth':{
            #         'account'           : target_employee.account,
            #         'name_kor'          : target_employee.name_kor,
            #         'name_eng'          : target_employee.name_eng,
            #         'nickname'          : target_employee.nickname,
            #         'rrn'               :str(rrn_decrypt),
            #         'mobile'            :target_employee.mobile,
            #         'emergency_num'     :target_employee.emergency_num,
            #         'company_email'     :target_employee.company_email,
            #         'personal_email'    :target_employee.personal_email,
            #         'bank_name'         :target_employee.bank_name,
            #         'bank_account'      :str(bank_account_decrypt),
            #         'passport_num'      :str(passport_num_decrypt),
            #         'address'           :target_employee.address,
            #         'detailed_address'  :target_employee.detailed_address
            #         },
            #     'admin_auth':{
            #         'joined_at'        : target_employee_detail.joined_at,
            #         'probation_period' : target_employee_detail.probation_period,
            #         'worked_since'     : target_employee_detail.worked_since,
            #         'total_experience' : target_employee_detail.total_experience,
            #         'annual_vacation'  : target_employee_detail.annual_vacation,
            #         'annual_vacation_permission' : target_employee_detail.annual_vacation_permission,
            #         'status'           : target_employee_detail.status,
            #         'promotion_date'   : target_employee_detail.promotion_date,
            #         'promoted_at'      : target_employee_detail.promoted_at,
            #         'pass_num'         : target_employee_detail.pass_num,
            #         'etc'              : target_employee_detail.etc
            #         }
            #     }
            # )
        # else:
        return JsonResponse(
            {
               'all_auth':{
                'account'           : target_employee.account,
                'name_kor'          : target_employee.name_kor,
                'name_eng'          : target_employee.name_eng,
                'nickname'          : target_employee.nickname,
                'rrn'               : str(rrn_decrypt),
                'mobile'            : target_employee.mobile,
                'emergency_num'     : target_employee.emergency_num,
                'company_email'     : target_employee.company_email,
                'personal_email'    : target_employee.personal_email,
                'bank_name'         : target_employee.bank_name,
                'bank_account'      : str(bank_account_decrypt),
                'passport_num'      : str(passport_num_decrypt),
                'address'           : target_employee.address,
                'detailed_address'  : target_employee.detailed_address 
            }
            }
        )
    
    def patch(self, request):
        try:
            data  = json.loads(request.body)
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if data.haskey('company_email') and not (re.search(regex, data['company_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if data.haskey('personal_email') and not (re.search(regex, data['personal_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if bcrypt.checkpw(data['password'].encode('UTF-8'), employee.password.encode('UTF-8')):
                if data.haskey('new_password'):
                    new_password       = data['new_password'].encode('utf-8')
                    new_password_crypt = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
                    
                    Employee(password = new_password_crypt)

                employee_field_list = [field.name for field in Employee._meta.get_fields()]
                employee_field_list.remove('password')

                employee_detail_field_list = [field.name for field in EmployeeDetail._meta.get_fields()]

                for field in employee_field_list:
                    if field in data:
                        if field == (rrn or bank_account or passport_num):
                            Employee.objects.update(**{field : encrypt_utils.encrypt(data[field], my_settings.SECRET.get('random'))})
                        else:
                            Employee.objects.update(**{field : data[field]})

                for field in employee_detail_field_list:
                    if field in data:
                        EmployeeDetail.objects.update(**{field : data[field]})

                return JsonResponse({"message": "MODIFICATION_SUCCESS"}, status=200)

            else:
                return JsonResponse({'message': "WRONG_PASSWORD"}, status=400)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)
