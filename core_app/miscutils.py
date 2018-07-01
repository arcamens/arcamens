from django.db.models.signals import pre_delete
from django.dispatch import receiver


def fmt_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )

# Signals.
def disk_cleaner(model):
    @receiver(pre_delete, sender=model)
    def delete_filewrapper(sender, instance, **kwargs):
        is_unique = model.objects.filter(file=instance.file)
        is_unique = is_unique.count() == 1
        print('being called')
        if is_unique: 
            instance.file.delete(save=False)

