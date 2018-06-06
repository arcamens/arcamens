import botos3

class S3BucketMiddleware:
     def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # file_fields = request.POST.getlist('s3file', [])
        # for field_name in file_fields:
            # paths = request.POST.getlist(field_name, [])
            # request.FILES.setlist(field_name, list(self.get_files_from_storage(paths)))

        request.FILES.setlist(field_name, list(self.get_files_from_storage(paths)))
        # we'll grab here the file names, create a bucket key(a specific one)
        # and weould just name it a key like 'user-id' name that maps too all files
        # that the user has in fact uploaded.
        return self.get_response(request)

        self.get_response = get_response

