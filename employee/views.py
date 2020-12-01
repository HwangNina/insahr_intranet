import os
import json
import bcrypt
import re
import jwt
import my_settings
import encrypt_utils
import jwt_utils
import requests
import boto3
import uuid

from django.http     import JsonResponse
from django.views    import View

from employee.models import Auth, Employee


# Create your views here.

class SignUpView(View):

    def post(self, request):
        try:
            data  = json.loads(request.body)

            if Employee.objects.filter(account=data['account']).exists():
                return JsonResponse({"message": "ACCOUNT_EXISTS"}, status=400)

            # password encryption
            password       = data['password'].encode('utf-8')
            password_crypt = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

            rrn_encrypted = encrypt_utils.encrypt(data['rrn'], my_settings.SECRET.get('random')).decode('utf-8')

            additional_infos = ['post_num', 'address', 'detailed_address']
            
            for index in range(0, len(additional_infos)):
                if additional_infos[index] in data:
                    additional_infos[index] = data[additional_infos[index]]
                else:
                    additional_infos[index] = None

            # insert record
            Employee(
                auth              = Auth.objects.get(id = 5),
                account           = data['account'],
                password          = password_crypt,
                name_kor          = data['name_kor'],
                name_eng          = data['name_eng'],
                rrn               = rrn_encrypted,
                mobile            = data['mobile'],
                post_num          = additional_infos[0],
                address           = additional_infos[1],
                detailed_address  = additional_infos[2],
                profile_image     = 'https://freepikpsd.com/wp-content/uploads/2019/10/default-profile-image-png-1-Transparent-Images.png'
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
                decryption_needed[idx] = None

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
                'post_num'          : target_employee['post_num'],
                'address'           : target_employee['address'],
                'detailed_address'  : target_employee['detailed_address'] 
            }
        )

    # @jwt_utils.signin_decorator
    def patch(self, request):
        try:
            data        = json.loads(request.body)
            # employee_id = request.employee.id
            employee_id = 4

            target_employee = Employee.objects.get(id = employee_id)

            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if ('company_email' in data and not (re.search(regex, data['company_email']))
                or 'personal_email' in data and not (re.search(regex, data['personal_email']))):
                return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

            if bcrypt.checkpw(data['password'].encode('UTF-8'), target_employee.password.encode('UTF-8')):
                if 'new_password' in data:
                    new_password       = data['new_password'].encode('utf-8')
                    new_password_crypt = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode('utf-8')
                    
                    target_employee.password = new_password_crypt
                    target_employee.save()

                employee_field_list = [field.name for field in Employee._meta.get_fields()]
                employee_field_list.remove('password')

                for field in employee_field_list:
                    if field in data:
                        if field in ['rrn', 'bank_account', 'passport_num']:
                            Employee.objects.filter(id = employee_id).update(**{field : encrypt_utils.encrypt(data[field], my_settings.SECRET.get('random')).decode('utf-8')})
                        else:
                            Employee.objects.filter(id = employee_id).update(**{field : data[field]})

                return JsonResponse({"message": "MODIFICATION_SUCCESS"}, status=200)

            else:
                return JsonResponse({'message': "WRONG_PASSWORD"}, status=400)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)


class ProfileImageView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=my_settings.AWS_ACCESS_KEY['MY_AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=my_settings.AWS_ACCESS_KEY['MY_AWS_SECRET_ACCESS_KEY']
    )
    # @jwt_utils.signin_decorator
    def post(self, request):
        try:
            # employee_id = request.employee.id
            employee_id = 4
    
            if request.FILES.get('attachment'):
                print('hi!')
                file = request.FILES.get('attachment')
                filename = str(uuid.uuid1()).replace('-','')
                self.s3_client.upload_fileobj(
                    file,
                    "thisisninasbucket",
                    filename,
                    ExtraArgs={
                        'ContentType':file.content_type
                    }
                )
                file_url = f"https://s3.ap-northeast-2.amazonaws.com/thisisninasbucket/{filename}"
            
            else:
                file_url = None
            
            target_employee               = Employee.objects.get(id = employee_id)
            print(file_url)
            target_employee.profile_image = file_url
            target_employee.save()

            return JsonResponse({'message': 'MODIFIACTION_SUCCESS'}, status=200)

        except KeyError as e :
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status=400)

    # @jwt_utils.signin_decorator
    def delete(self, request):
        # employee_id = request.employee.id
        employee_id = 4

        target_employee               = Employee.objects.get(id = employee_id)
        target_employee.profile_image = 'https://freepikpsd.com/wp-content/uploads/2019/10/default-profile-image-png-1-Transparent-Images.png'
        target_employee.save()

        return JsonResponse({'message':'DELETED'}, status=200)
        