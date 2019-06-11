# Arcamens

Kanban Boards, Super Backlogs with Cut&amp;Paste and new perspective of boards, lists, cards.
Arcamens is a robust and powerful project management platform whose goal is optmizing busines's workflow.
It is extremely versatile when dealing with high payloads of tasks.

Arcamens integrates with github and bitbucket. Cards can be referenced from commits and card
notes are created. One can easily search for cards based on its associated commits.

The UI works alike in both desktop or mobiles it is super intuitive also doesn't demand
a long time to get acquainted to.

The search mechanism is extremely handy it allows one to filter posts, cards, notes, comments
based on multiple criterias.

The boards are visualized in a tree-like manner, boards, lists, cards are displayed along
four columns. Such a perspective of boards allow a nifty management of information due to the
Cut&Paste concept instead of the usual Drag&Drop.

# Features

* Powerful Event System 

* Event Feedback

* Facebook-like Groups 

* Superbacklog 

* Flexible Search Mechanism
 
* Flexible Boards Perspective

* Extensibility

* Mobile Responsive

* Workspaces

* Public/Private Organizations

# Setup/Development

First it is necessary to setup a virtualenv.

~~~
# Create a virtualenv folder in case you don't already have it.
~/.virtualenvs/
cd ~/.virtualenvs/
virtualenv arcamens -p python3.5
~~~

Activate the virtualenv.

~~~
cd ~/projects/arcamens-code
source arcamens/bin/activate
~~~

Now it is necessary to install the requirements.

~~~~
pip install -r requirements.txt 
~~~~

The steps below show how to get Arcamens running for development.

~~~
cd ~/projects/arcamens-code
python manage.py blowdb

# Create the django admin site super user arcamens.
./create-superusers

# This script is used to create random objects for testing.
./build-data

stdbuf -o 0 python manage.py runserver 0.0.0.0:8000
~~~

Once that is done just access http://0.0.0.0:8000 

Login with.

~~~
email developer@arcamens.com
password arcamens
~~~


# History

Arcamens concepts were conceived by me when i was working with Victor Porton in the spec of another platform.
I had such an insight due to disliking so much other project management platform that we were using by the time.

Victor Porton has given feedback about features, tested code also helped to implement django-paybills package
which is the paypal module.


