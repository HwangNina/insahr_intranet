# autopep8: off
import os
import jwt
import json
import my_settings

from pathlib                import Path
from django.http            import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from employee.models        import Employee


def signin_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token     = request.headers.get('Authorization', None)

            # admin_key       = my_settings.SECRET.get('admin_secret')
            # employee_key    = my_settings.SECRET.get('admin_secret')
            # probition_key   = my_settings.SECRET.get('probition_secret')
            # parttime_key    = my_settings.SECRET.get('parttime_secret')
            # freelancer_key  = my_settings.SECRET.get('freelancer_secret')

            # algorithm = my_settings.SECRET.get('JWT_ALGORITHM')

            # if token == None:
            #     return JsonResponse({"message" : "TOKEN_DOES_NOT_EXIST"}, status=403)

            # key_list = [admin_key,employee_key,probition_key,parttime_key,freelancer_key]
            
            # for k in key_list:
            #     decode = jwt.decode(token, k, algorithm = algorithm)
            #     if Employee.objects.filter(id = decode['employee']).exists:
            #         request.employee = employee

            key = my_settings.SECRET.get('secret_key')

            algorithm = my_settings.SECRET.get('JWT_ALGORITHM')

            if token == None:
                return JsonResponse({"message" : "TOKEN_DOES_NOT_EXIST"}, status=403)

            decode = jwt.decode(token, key, algorithm = algorithm)
            
         Conflicting files
employee/views.pyxcept User.DoesNotExist:
            return JsonResponse({'message': 'USER_DOES_NOT_EXIST'}, status=403)

        return func(self, request, *args, **kwargs)

    return wrapper
