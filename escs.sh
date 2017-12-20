##############################################################################
# push arcamens.alpha development branch.
cd ~/projects/arcamens.alpha-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;
rm -fr ~/projects/arcamens.alpha-code/static/media
git status
git add *
git commit -a
git push -u origin development
##############################################################################

# push, arcamens.alpha, master.
cd ~/projects/arcamens.alpha-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;

git status
git add *
git commit -a
git push -u origin master
##############################################################################
# create dev branch.
cd ~/projects/arcamens.alpha-code
git branch -a
git checkout -b development
git push --set-upstream origin development
##############################################################################
# push, arcamens.alpha, beta.
cd ~/projects/arcamens.alpha-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;
git status
git add *
git commit -a
git push -u origin beta
##############################################################################
# merge, dev, into, master:
git checkout master
git merge development
git push -u origin master
git checkout development
##############################################################################
# merge, beta, into, alpha:
git checkout alpha
git merge beta
git push -u origin alpha
git checkout beta

##############################################################################
# merge, beta, into, master:
git checkout master
git merge beta
git push -u origin master
git checkout beta
##############################################################################
# merge, beta, into, alpha:
git checkout alpha
git merge beta
git push -u origin alpha
git checkout beta
##############################################################################

# merge, alpha, into, master:
git checkout master
git merge alpha
git push -u origin master
git checkout alpha
##############################################################################
# merge, alpha, into, master:
git checkout alpha
git merge master
git push -u origin alpha
git checkout alpha
##############################################################################

# arcamens.alpha, pull.
cd ~/projects/arcamens.alpha-code
git pull
##############################################################################
# setup, admin, site.
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | python manage.py shell
##############################################################################
# make migrations.
cd ~/projects/arcamens.alpha-code
python manage.py blowdb
./build-data

# create, arcamens.alpha, alpha, branch.
git checkout -b alpha
git push --set-upstream origin alpha

# create, arcamens.alpha, beta, branch.
git checkout -b beta
git push --set-upstream origin beta

##############################################################################
# switch, alpha, branch.
git checkout alpha
##############################################################################
# switch, beta, branch.
git checkout beta

##############################################################################
# run, arcamens.alpha, server, debugging.
cd ~/projects/arcamens.alpha-code
stdbuf -o 0 python manage.py runserver 0.0.0.0:8000
##############################################################################
# clone, arcamens.alpha, wiki.

cd ~/projects
git clone git@bitbucket.org:iogf/arcamens.alpha.git/wiki arcamens.alpha.wiki-code

##############################################################################
# create, setup, virtualenv, arcamens.alpha.
cd ~/.virtualenvs/
ls -la
# by default, python3 has executable named python in arch linux.
virtualenv arcamens.alpha -p /usr/bin/python
##############################################################################
# activate, virtualenv, arcamens.alpha.
cd ~/.virtualenvs/
source arcamens.alpha/bin/activate
cd ~/projects/arcamens.alpha-code
##############################################################################
# install, arcamens.alpha, dependencies, virtualenv.
cd ~/.virtualenvs/
source arcamens.alpha/bin/activate
cd ~/projects/arcamens.alpha-code
pip install -r requirements.txt 
##############################################################################
# create, arcamens.alpha, project.
cd ~/projects/
django-admin startproject arcamens.alpha arcamens.alpha-code
##############################################################################
# create, core_app, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp core_app
##############################################################################
# create, help_app, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp help_app
##############################################################################
# create, register_app, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp register_app

##############################################################################
# create, timeline, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp post_app
##############################################################################
# create, chat_app, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp chat_app
##############################################################################
# create, comment_app, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp comment_app


##############################################################################
# create, timeline_app, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp timeline_app
##############################################################################
# create, stream, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp stream_app
##############################################################################
# rename, customer, to user.

cd ~/projects/arcamens.alpha-code
grep -rl 'board_app.Organization' --exclude-dir='.git' ./ | xargs sed -i 's/board_app.Organization/core_app.Organization/g'

grep -rl 'core_app.Organization' --exclude-dir='.git' ./ | xargs sed -i 's/board_app.Organization/core_app.Organization/g'

cd ~/projects/labor2-code

grep -rl 'timeline_app\.User' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app\.User/core_app.User/g'

grep -rl 'user-settings' --exclude-dir='.git' ./ | xargs sed -i 's/user-settings/list-user-tags/g'

grep -rl 'timeline_app:list-timelines' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app:list-timelines/timeline_app:list-timelines/g'

cd ~/projects/arcamens.alpha-code

grep -rl 'core_app:profile' --exclude-dir='.git' ./ | xargs sed -i 's/core_app:profile/board_app:profile/g'


cd ~/projects/arcamens.alpha-code

grep -rl 'default_organization' --exclude-dir='.git' ./ | xargs sed -i 's/default_organization/default/g'

cd ~/projects/arcamens.alpha-code/board_app/

grep -rl 'timeline_app/' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app\//board_app\//g'

grep -rl 'timeline_app' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app/timeline_app/g'

cd ~/projects/arcamens.alpha-code/board_app/

grep -rl 'timeline_app/' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app\//board_app\//g'

cd ~/projects/arcamens.alpha-code/list_app

grep -rl 'core_app\.models' --exclude-dir='.git' ./ | xargs sed -i 's/core_app\.models/board_app.models/g'

grep -rl 'core_app\.arcamens.alpha' --exclude-dir='.git' ./ | xargs sed -i 's/core_app\.arcamens.alpha/timeline_app\.arcamens.alpha/g'

cd ~/projects/arcamens.alpha-code/board_app

grep -rl 'core_app\.models' --exclude-dir='.git' ./ | xargs sed -i 's/core_app\.models/board_app.models/g'

cd ~/projects/labor2-code

grep -rl 'Organization' --exclude-dir='.git' ./ | xargs sed -i 's/Organization/arcamens.alpha/g'

cd ~/projects/arcamens.alpha-code/timeline_app

grep -rl 'core_app:' --exclude-dir='.git' ./ | xargs sed -i 's/core_app:/timeline_app:/g'

cd ~/projects/arcamens.alpha-code/board_app

grep -rl 'core_app:' --exclude-dir='.git' ./ | xargs sed -i 's/core_app:/board_app:/g'


cd ~/projects/arcamens.alpha-code/board_app

grep -rl '#main-view' --exclude-dir='.git' ./ | xargs sed -i 's/#main-view/#main-viewport/g'

grep -rl '#main-view' --exclude-dir='.git' ./ | xargs sed -i 's/#main-view/#main-viewport/g'


grep -rl 'Comment' --exclude-dir='.git' ./ | xargs sed -i 's/Comment/PostComment/g'

grep -rl 'UserFilter' --exclude-dir='.git' ./ | xargs sed -i 's/UserFilter/arcamens.alphaUserFilter/g'

grep -rl 'Event' --exclude-dir='.git' ./ | xargs sed -i 's/Event/arcamens.alphaEvent/g'

grep -rl 'customer' --exclude-dir='.git' ./ | xargs sed -i 's/customer/user/g'

cd ~/projects/arcamens.alpha-code/timeline_app

grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens.alpha-code/post_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens.alpha-code/post_comment_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens.alpha-code/site_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens.alpha-code/card_comment_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/board_app/g'

cd ~/projects/arcamens.alpha-code/post_app
grep -rl 'FileWrapper' --exclude-dir='.git' ./ | xargs sed -i 's/FileWrapper/PostFileWrapper/g'

cd ~/projects/arcamens.alpha-code/card_app
grep -rl 'FileWrapper' --exclude-dir='.git' ./ | xargs sed -i 's/FileWrapper/CardFileWrapper/g'

cd ~/projects/arcamens.alpha-code/board_app
grep -rl 'FileWrapper' --exclude-dir='.git' ./ | xargs sed -i 's/FileWrapper/CardFileWrapper/g'


##############################################################################
# delete, last, commit.

cd ~/projects/arcamens.alpha-code
git reset HEAD^ --hard
git push -f
##############################################################################
# checkout, changed, files, between, two, branches.

git diff --name-status alpha beta
##############################################################################
# merge, specific, file, from alpha.

git checkout beta 
git checkout alpha path-to-file
git commit -a
##############################################################################
# unversion, file, git, db.sqlite3.

git rm --cached db.sqlite3
git rm --cached arcamens.alpha/settings.py
##############################################################################
# create, signup_app, app.
cd ~/projects/arcamens.alpha-code
python manage.py startapp site_app
##############################################################################
# delete, beta, branch.

cd ~/projects/arcamens.alpha-code
git branch -d beta
git push origin :beta
git fetch -p 
##############################################################################
# delete, alpha, branch.

cd ~/projects/arcamens.alpha-code
git branch -d alpha
git push origin :alpha
git fetch -p 

##############################################################################
# create, first, release, test, tag.

git tag -a 0.0.1 -m 'Initial release'
git push origin : 0.0.1
##############################################################################
# create, first, release, test, tag.

git tag -a 0.0.13 -m 'A better release.'
git push origin : 0.0.13
##############################################################################

# create, first, release, test, tag.

git tag -a 0.0.1 -m 'Initial release'
git push origin : 0.0.1
##############################################################################

# delete, 0.0.1, tag
git tag -d 0.0.1
git push --delete origin 0.0.1
##############################################################################
# delete, 0.0.2, tag
git tag -d 0.0.2
git push --delete origin 0.0.2
##############################################################################
# create, 0.0.4, release, test, tag.

git tag -a 0.0.4 -m 'A more functional release with event system partially implemented.'
##############################################################################
git push origin : 0.0.5
# create, 0.0.4, release, test, tag.

git tag -a 0.0.5 -m 'Changing font size for displaying timelines.'
git push origin : 0.0.5

##############################################################################
git push origin : 0.0.6
# create, 0.0.4, release, test, tag.

git tag -a 0.0.6 -m 'Fixing UI.'
git push origin : 0.0.6

##############################################################################
git push origin : 0.0.7
# create, 0.0.7, release, test, tag.

git tag -a 0.0.7 -m 'Adding truncate for timeline name.'
git push origin : 0.0.7
##############################################################################
git push origin : 0.0.8
# create, 0.0.8, release, test, tag.

git tag -a 0.0.8 -m 'Adding view for updating timeline.'
git push origin : 0.0.8
##############################################################################
git push origin : 0.0.9
# create, 0.0.9, release, test, tag.

git tag -a 0.0.9 -m 'Adding view for updating timeline.'
git push origin : 0.0.9
##############################################################################
git push origin : 0.0.10
# create, 0.0.9, release, test, tag.

git tag -a 0.0.10 -m 'Improving UI, adding navigation button.'
git push origin : 0.0.10
##############################################################################
git push origin : 0.0.11
# create, 0.0.11, release, test, tag.

git tag -a 0.0.11 -m 'Improving UI, adding navigation button.'
git push origin : 0.0.11
##############################################################################

# create, first, release, 0.0.2, tag.

git tag -a 0.0.2 -m 'Implementation of card_app, it remains doing enhancements.'
git push origin : 0.0.2


cd ~/Downloads
ls
unzip iogf-arcamens.alpha-2a985217fd3d.zip
ls
cd iogf-arcamens.alpha-2a985217fd3d
ls

stdbuf -o 0 python manage.py runserver 0.0.0.0:8000 
cd ~
##############################################################################
cd ~/projects/arcamens.alpha-code

# rename card_app to markdown_app.
grep -rl  'card_app' . | xargs sed -i 's/card_app/markdown_app/g' 
grep -rl  'Card' . | xargs sed -i 's/Card/Markdown/g' 
grep -rl  'card' . | xargs sed -i 's/card/markdown/g' 

##############################################################################
#fix #gitignore #remove #cached #files #ignore #folder #migrations

git rm -r --cached ./*/migrations/
git rm --cached db.sqlite3

##############################################################################
# install django-jdrop.
cd ~/projects/django-jdrop-code
python setup.py install

# uninstall django-jdrop.
pip uninstall django-jdrop
y

pip install paho-mqtt
pip install pika

##############################################################################

wget --post-data='somedata' http://189.84.248.176:8000/register_app/paypal-ipn/
##############################################################################
# install paybills in virtualenv.
cd ~/.virtualenvs/
source arcamens.alpha/bin/activate
cd ~/projects/django-paybills-code
python setup.py install
rm -fr build
##############################################################################

# access victor server through ssh.

tee -i >(stdbuf -o 0 ssh arcamens.alpha-test@job-lab.net 'bash -i')

# accept signals.
tee >(stdbuf -o 0 ssh arcamens.alpha-test@job-lab.net 'bash -i')

# run as supervisord.
supervisord -n -c ../conf/supervisord.conf

# remove arcamens.alpha and paybills.
rm -fr /home/arcamens.alpha-test/projects/arcamens.alpha-code
rm -fr /home/arcamens.alpha-test/projects/django-paybills-code
##############################################################################
# install paybills
cd ~/projects/django-paybills-code
python setup.py install

##############################################################################
# deploy arcamens.alpha on victor server.

cp -R ~/projects/arcamens.alpha-code /tmp
rm -fr /tmp/arcamens.alpha-code/.git
find /tmp/arcamens.alpha-code -path "arcamens.alpha-code/**/migrations/*.py" -not -name "__init__.py" -delete
find /tmp/arcamens.alpha-code -path "arcamens.alpha-code/**/migrations/*.pyc" -not -name "__init__.py" -delete
find /tmp/arcamens.alpha-code -path "arcamens.alpha-code*/*.pyc" -not -name "__init__.py" -delete
find /tmp/arcamens.alpha-code -name "db.sqlite3" -delete

# use rsync.
rsync -r /tmp/arcamens.alpha-code arcamens.alpha-test@job-lab.net:/home/arcamens.alpha-test/projects

# uses scp.
scp -r /tmp/arcamens.alpha-code arcamens.alpha-test@job-lab.net:/home/arcamens.alpha-test/projects

# remove the old code.
ssh arcamens.alpha-test@job-lab.net '
rm -fr /home/arcamens.alpha-test/projects/arcamens.alpha-code'

##############################################################################
# install paybills on victor server.

cp -R ~/projects/django-paybills-code /tmp
rm -fr /tmp/django-paybills-code/.git

scp -r /tmp/django-paybills-code arcamens.alpha-test@job-lab.net:/home/arcamens.alpha-test/projects

ssh arcamens.alpha-test@job-lab.net '
cd ~/.virtualenvs/
source arcamens.alpha/bin/activate
cd /home/arcamens.alpha-test/projects/django-paybills-code
sudo python setup.py install'

# create basic folders victor porton server.
mkdir ~/.virtualenvs
mkdir ~/projects
##############################################################################

pip install future
apt-get install rabbitmq
##############################################################################
#delete #remove #virtualenv
cd ~/.virtualenvs/
rm -fr arcamens.alpha
##############################################################################
# install blowdb
cd ~/projects/django-blowdb-code
python setup.py install
rm -fr build

##############################################################################







