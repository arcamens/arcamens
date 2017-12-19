# README #

# Development standards

#### Template names

Template names should be named as follow:

~~~
view-name.html
~~~

Templates which are included in a given view should be named as:

~~~
view-name-template-name.html
~~~

In this way, it is easy to know where the template is rendered
and if it is included then where it is included.

Templates which are included in more than one template
should follow:

~~~
utils-template-name.html
~~~

#### Form names

Forms which are inherited from ModelForm should be named as follow:

ModelNameForm

When there are more than two forms that are used
in different views:

~~~python
class ViewNameModelNameForm(forms.ModelForm):
~~~

#### View type/names

It should be used just generic views.

~~~python
from django.views.generic import View
~~~

Views that change state of models should be named as follow:

~~~python
class ActionModelName
~~~

#### Url names


#### Models

**Mixins**


