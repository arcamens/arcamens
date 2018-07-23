from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

class RenderExc(Exception):
    def __init__(self, template, context, status=200):
        self.template = template
        self.context  = context
        self.status   = status

class ExceptionToResponse(MiddlewareMixin):
    def process_exception(self, request, exception):
        print('This method should be called when an exception occurs.')
        if isinstance(exception, (RenderExc,)):
            return render(request, exception.template, 
                exception.context, status=exception.status)
