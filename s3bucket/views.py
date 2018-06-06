from django.shortcuts import render
from django.views.generic import View
from . import forms
from . import models

class UpdateObjectView(View):
    def get(self, request, obj_id):
        obj = models.Obj.objects.get(id=obj_id)

        return render(request,
        'app/template.html', {'company': company,
        'form': forms.ObjForm(instance=obj)})

    def post(self, request, obj_id):
        obj  = models.Obj.objects.get(id=obj_id)
        form = forms.ObjForm(request.POST, instance=obj)

        if not form.is_valid():
            return render(request, 'app/template.html',
                {'form': form})

        form.save()

        return render(request,
        'app/template-success.html', {})



