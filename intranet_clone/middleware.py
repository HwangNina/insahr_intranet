import json

from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin

class PutParsingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == "PATCH" and request.content_type != "application/json":
            if hasattr(request, '_post'):
                del request._post
                del request._files
            try:
                request.method = "POST"
                request._load_post_and_files()
                request.method = "PATCH"
            except AttributeError as e:
                request.META['REQUEST_METHOD'] = 'POST'
                request._load_post_and_files()
                request.META['REQUEST_METHOD'] = 'PATCH'

            request.PATCH = request.POST


class JSONParsingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (request.method == "PATCH" or request.method == "POST") and request.content_type == "application/json":
            try:
                request.JSON = json.loads(request.body)
            except ValueError as ve:
                return HttpResponseBadRequest("unable to parse JSON data. Error : {0}".format(ve))