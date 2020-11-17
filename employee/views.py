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
from employee.models            import Employee
from django.http            import JsonResponse

# Create your views here.
class SignUpView(View):

    @signin_decorator
    def post(self, request):
        try:
            data  = json.loads(request.body)
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if not (re.search(regex, data['company_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if not (re.search(regex, data['personal_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if Employee.objects.filter(account=data['account']).exists():
                return JsonResponse({"message": "ACCOUNT_EXISTS"}, status=400)

            password       = data['password'].encode('utf-8')
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

            rrn_encrypt = encrypt_utils.encrypt(data['rrn'], my_settings.SECRET.get('raw'))
           
            bank_account_encrypt = encrypt_utils.encrypt(data['bank_account'], my_settings.SECRET.get('raw'))

            passport_num_encrypt = encrypt_utils.encrypt(data['passport_num'], my_settings.SECRET.get('raw'))

            Employee(
                auth             = Auth.objects.get(id = data['auth']),
                account          = data['account'],
                password         = password_crypt,
                name_kor         = data['name_kor'],
                name_eng         = data['name_eng'],
                nickname         = data['nickname'],
                rrn              = rrn_encrypt.decode('utf-8'),
                mobile           = data['mobile'],
                emergency_num    = data['emergency_num'],
                company_email    = data['company_email'],
                personal_email   = data['personal_email'],
                bank_name        = data['bank_name'],
                bank_account     = bank_account_encrypt.decode('utf-8'),
                passport_num     = passport_num_encrypt.decode('utf-8'),
                address          = data['address'],
                detailed_address = data['detailed_address'],
            ).save()

            EmployeeDetail(
                joined_at        = data['joined_at']
                probation_period = data['probation_period']
                worked_since     = data['worked_since']
                total_experience = data['total_experience']
                annual_vacation  = data['annual_vacation']
                annual_vacation_permission = data['annual_vacation_permission']
                status           = data['status']
                promotion_date   = data['promotion_date']
                promoted_at      = data['promoted_at']
                pass_num         = data['pass_num']
                etc              = data['etc']
            ).save()

            return JsonResponse({"message": "SIGNUP_SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)

        except ValueError:
            return JsonResponse({"message": "VALUE_ERROR"}, status=400)


class SignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            employee = Employee.objects.get(account=data['account'])

            if bcrypt.checkpw(data['password'].encode('UTF-8'), employee.password.encode('UTF-8')):
                admin_key       = my_settings.SECRET.get('admin_secret')
                employee_key    = my_settings.SECRET.get('admin_secret')
                probition_key   = my_settings.SECRET.get('probition_secret')
                parttime_key    = my_settings.SECRET.get('parttime_secret')
                freelancer_key  = my_settings.SECRET.get('freelancer_secret')

                algorithm       = my_settings.SECRET.get('JWT_ALGORITHM')

                if employee.auth == 1:
                    key = admin_key
                if employee.auth == 2:
                    key = employee_key
                if employee.auth == 3:
                    key = probition_key
                if employee.auth == 4:
                    key = parttime_key
                if employee.auth == 5:
                    key = freelancer_key

                token     = jwt.encode({'user' : user.id},key, algorithm = algorithm).decode('UTF-8')
                return JsonResponse({"token": token, "message": "SIGNIN_SUCCESS", "name" : user.name}, status=200)

            else:
                return JsonResponse({"message": "INVALID_PASSWORD"}, status=401)

        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)

        except ValueError:
            return JsonResponse({"message": "VALUE_ERROR"}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"message": "INVALID_USER"}, status=401)


class EmployeeInfoView(View):

    # @decorator
    def get(self, request):
        data            = json.loads(request.body)
        target_employee = Employee.objects.get(id = data['employee'])

        rrn_decrypt          = encrypt_utils.decrypt(
                               target_employee.rrn, my_settings.SECRET.get('random')
                               ).decode('utf-8')
        bank_account_decrypt = encrypt_utils.decrypt(
                               target_employee.bank_account, my_settings.SECRET.get('random')
                               ).decode('utf-8')
        passport_num_decrypt = encrypt_utils.decrypt(
                               target_employee.passport_num, my_settings.SECRET.get('random')
                               ).decode('utf-8')

        return JsonResponse(
            {
            'account': target_employee.account,
            'name_kor': target_employee.name_kor,
            'name_eng': target_employee.name_eng,
            'nickname': target_employee.nickname,
            'rrn':str(rrn_decrypt),
            'mobile':target_employee.mobile,
            'emergency_num':target_employee.emergency_num,
            'company_email':target_employee.company_email,
            'personal_email':target_employee.personal_email,
            'bank_name':target_employee.bank_name,
            'bank_account':str(bank_account_decrypt),
            'passport_num':str(passport_num_decrypt),
            'address':target_employee.address,
            'detailed_address':target_employee.detailed_address
            }
        )
    
    # @decorator
    def patch(self, request):
        try:
            data  = json.loads(request.body)
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if not (re.search(regex, data['company_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if not (re.search(regex, data['personal_email'])):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if data['password'] != 

            password       = data['password'].encode('utf-8')
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

            rrn_encrypt = encrypt_utils.encrypt(data['rrn'], my_settings.SECRET.get('raw'))
           
            bank_account_encrypt = encrypt_utils.encrypt(data['bank_account'], my_settings.SECRET.get('raw'))

            passport_num_encrypt = encrypt_utils.encrypt(data['passport_num'], my_settings.SECRET.get('raw'))

            Employee(
                account          = data['account'],
                password         = password_crypt,
                name_kor         = data['name_kor'],
                name_eng         = data['name_eng'],
                nickname         = data['nickname'],
                rrn              = rrn_encrypt.decode('utf-8'),
                mobile           = data['mobile'],
                emergency_num    = data['emergency_num'],
                company_email    = data['company_email'],
                personal_email   = data['personal_email'],
                bank_name        = data['bank_name'],
                bank_account     = bank_account_encrypt.decode('utf-8'),
                passport_num     = passport_num_encrypt.decode('utf-8'),
                address          = data['address'],
                detailed_address = data['detailed_address']
            ).save()

            return JsonResponse({"message": "SIGNUP_SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)

        except ValueError:
            return JsonResponse({"message": "VALUE_ERROR"}, status=400)