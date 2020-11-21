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
            key       = my_settings.SECRET.get('SECRET_KEY')
            algorithm = my_settings.SECRET.get('JWT_ALGORITHM')

            if token == None:
                return JsonResponse({"message" : "TOKEN_DOES_NOT_EXIST"}, status=403)

           
            decode = jwt.decode(token, key, algorithm = algorithm)
            request.employee = Employee.objects.get(id = decode['employee'])

        except User.DoesNotExist:
            return JsonResponse({'message': 'USER_DOES_NOT_EXIST'}, status=403)

        return func(self, request, *args, **kwargs)

    return wrapper
