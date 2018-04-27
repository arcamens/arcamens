##############################################################################
# push arcamens alpha branch.
cd ~/projects/arcamens-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;
rm -fr ~/projects/arcamens-code/static/media
git status
git add *
git commit -a
git push -u origin staging
##############################################################################
# push arcamens alpha branch.
cd ~/projects/arcamens-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;
rm -fr ~/projects/arcamens-code/static/media
git status
git add *
git commit -a
git push -u origin alpha

##############################################################################
# push arcamens on master.
cd ~/projects/arcamens-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;

git status
git add *
git commit -a
git push -u origin master
##############################################################################
# create dev branch.
cd ~/projects/arcamens-code
git branch -a
git checkout -b development
git push --set-upstream origin development
##############################################################################
# push, arcamens, beta.
cd ~/projects/arcamens-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;
git status
git add *
git commit -a
git push -u origin beta
##############################################################################
# merge staging into master.
git checkout master
git merge staging
git push -u origin master
git checkout staging
##############################################################################
# merge master into staging.
git checkout staging
git merge master
git push -u origin staging
git checkout staging

##############################################################################
# merge master into stable.
git checkout stable
git merge master
git push -u origin stable
git checkout master


##############################################################################
# checkout all.

git checkout *

##############################################################################
# merge alpha into staging.
git checkout staging
git merge alpha
git push -u origin staging
git checkout staging

git branch -d alpha
git push origin :alpha
git fetch -p 

##############################################################################

# arcamens, pull.
cd ~/projects/arcamens-code
git pull
##############################################################################
# setup, admin, site.
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | python manage.py shell
##############################################################################
# make migrations.
cd ~/projects/arcamens-code
python manage.py blowdb
./build-data
##############################################################################
# stress-db.
./stress-db teta 1
##############################################################################


# create, arcamens, alpha, branch.
git checkout -b alpha
git push --set-upstream origin alpha

# create, arcamens, beta, branch.
git checkout -b beta
git push --set-upstream origin beta

git checkout -b gamma
git push --set-upstream origin gamma

##############################################################################
# switch, alpha, branch.
git checkout alpha
##############################################################################
# switch, beta, branch.
git checkout beta

##############################################################################
# run arcamens project.
cd ~/projects/arcamens-code
stdbuf -o 0 python manage.py runserver 0.0.0.0:8000

#####k#########################################################################
# clone, arcamens, wiki.

cd ~/projects
git clone git@bitbucket.org:iogf/arcamens.git/wiki arcamens.wiki-code

##############################################################################
# create, setup, virtualenv, arcamens.
cd ~/.virtualenvs/
ls -la
# by default, python3 has executable named python in arch linux.
virtualenv arcamens -p /usr/bin/python
##############################################################################
# activate, virtualenv, arcamens.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/arcamens-code
##############################################################################
# install, arcamens, dependencies, virtualenv.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/arcamens-code
pip install -r requirements.txt 
##############################################################################
# create, arcamens, project.
cd ~/projects/
django-admin startproject arcamens arcamens-code
##############################################################################
# create, core_app, app.
cd ~/projects/arcamens-code
python manage.py startapp core_app
##############################################################################
# create, help_app, app.
cd ~/projects/arcamens-code
python manage.py startapp help_app
##############################################################################
# create, register_app, app.
cd ~/projects/arcamens-code
python manage.py startapp register_app

##############################################################################
# create, timeline, app.
cd ~/projects/arcamens-code
python manage.py startapp post_app
##############################################################################
# create, chat_app, app.
cd ~/projects/arcamens-code
python manage.py startapp chat_app
##############################################################################
# create, comment_app, app.
cd ~/projects/arcamens-code
python manage.py startapp comment_app


##############################################################################
# create, timeline_app, app.
cd ~/projects/arcamens-code
python manage.py startapp timeline_app
##############################################################################
# create, stream, app.
cd ~/projects/arcamens-code
python manage.py startapp stream_app
##############################################################################
# rename, customer, to user.

cd ~/projects/arcamens-code
grep -rl 'board_app\.models\.User' --exclude-dir='.git' ./ | xargs sed -i 's/board_app\.models\.User/core_app.models.User/g'

grep -rl 'OrganizationEvent' --exclude-dir='.git' ./ | xargs sed -i 's/OrganizationEvent/Event/g'

grep -rl 'board_app.Labor' --exclude-dir='.git' ./ | xargs sed -i 's/board_app.Labor/core_app.Organization/g'

grep -rl 'timeline_app.Opus' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app.Opus/core_app.Organization/g'

grep -rl '\.opus' --exclude-dir='.git' ./ | xargs sed -i 's/\.opus//g'
grep -rl '\.labor' --exclude-dir='.git' ./ | xargs sed -i 's/\.labor//g'

grep -rl 'Labor' --exclude-dir='.git' ./ | xargs sed -i 's/Labor/Organization/g'
grep -rl 'Opus' --exclude-dir='.git' ./ | xargs sed -i 's/Opus/Organization/g'

cd ~/projects/labor2-code

grep -rl 'timeline_app\.User' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app\.User/core_app.User/g'

grep -rl 'user-settings' --exclude-dir='.git' ./ | xargs sed -i 's/user-settings/list-user-tags/g'

grep -rl 'timeline_app:list-timelines' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app:list-timelines/timeline_app:list-timelines/g'

cd ~/projects/arcamens-code

grep -rl 'core_app:profile' --exclude-dir='.git' ./ | xargs sed -i 's/core_app:profile/board_app:profile/g'


cd ~/projects/arcamens-code

grep -rl 'default_organization' --exclude-dir='.git' ./ | xargs sed -i 's/default_organization/default/g'

cd ~/projects/arcamens-code/board_app/

grep -rl 'timeline_app/' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app\//board_app\//g'

grep -rl 'timeline_app' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app/timeline_app/g'

cd ~/projects/arcamens-code/board_app/

grep -rl 'timeline_app/' --exclude-dir='.git' ./ | xargs sed -i 's/timeline_app\//board_app\//g'

cd ~/projects/arcamens-code/list_app

grep -rl 'core_app\.models' --exclude-dir='.git' ./ | xargs sed -i 's/core_app\.models/board_app.models/g'

grep -rl 'core_app\.arcamens' --exclude-dir='.git' ./ | xargs sed -i 's/core_app\.arcamens/timeline_app\.arcamens/g'

cd ~/projects/arcamens-code/board_app

grep -rl 'core_app\.models' --exclude-dir='.git' ./ | xargs sed -i 's/core_app\.models/board_app.models/g'

cd ~/projects/labor2-code

grep -rl 'Organization' --exclude-dir='.git' ./ | xargs sed -i 's/Organization/arcamens/g'

cd ~/projects/arcamens-code/timeline_app

grep -rl 'core_app:' --exclude-dir='.git' ./ | xargs sed -i 's/core_app:/timeline_app:/g'

cd ~/projects/arcamens-code/board_app

grep -rl 'core_app:' --exclude-dir='.git' ./ | xargs sed -i 's/core_app:/board_app:/g'


cd ~/projects/arcamens-code/board_app

grep -rl '#main-view' --exclude-dir='.git' ./ | xargs sed -i 's/#main-view/#main-viewport/g'

grep -rl '#main-view' --exclude-dir='.git' ./ | xargs sed -i 's/#main-view/#main-viewport/g'


grep -rl 'Comment' --exclude-dir='.git' ./ | xargs sed -i 's/Comment/PostComment/g'

grep -rl 'UserFilter' --exclude-dir='.git' ./ | xargs sed -i 's/UserFilter/arcamensUserFilter/g'

grep -rl 'Event' --exclude-dir='.git' ./ | xargs sed -i 's/Event/arcamensEvent/g'

grep -rl 'customer' --exclude-dir='.git' ./ | xargs sed -i 's/customer/user/g'

cd ~/projects/arcamens-code/timeline_app

grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens-code/post_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens-code/post_comment_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens-code/site_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/timeline_app/g'

cd ~/projects/arcamens-code/card_comment_app
grep -rl 'core_app' --exclude-dir='.git' ./ | xargs sed -i 's/core_app/board_app/g'

cd ~/projects/arcamens-code/post_app
grep -rl 'FileWrapper' --exclude-dir='.git' ./ | xargs sed -i 's/FileWrapper/PostFileWrapper/g'

cd ~/projects/arcamens-code/card_app
grep -rl 'FileWrapper' --exclude-dir='.git' ./ | xargs sed -i 's/FileWrapper/CardFileWrapper/g'

cd ~/projects/arcamens-code/board_app
grep -rl 'FileWrapper' --exclude-dir='.git' ./ | xargs sed -i 's/FileWrapper/CardFileWrapper/g'


##############################################################################
# delete, last, commit.

cd ~/projects/arcamens-code
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
git rm --cached arcamens/settings.py
##############################################################################
# create, signup_app, app.
cd ~/projects/arcamens-code
python manage.py startapp site_app
##############################################################################
# delete, beta, branch.

cd ~/projects/arcamens-code
git branch -d beta
git push origin :beta
git fetch -p 

##############################################################################

# delete, gamma, branch.

cd ~/projects/arcamens-code
git branch -d gamma
git push origin :gamma
git fetch -p 

##############################################################################
# delete alpha branch.

cd ~/projects/arcamens-code
git branch -d alpha
git push origin :alpha
git fetch -p 

##############################################################################
# create releases.

git checkout master
git tag -a 1.0.1 -m 'Getting list-logs view to work with pagination.'
git push origin : 1.0.1
git checkout staging

git checkout master
git tag -a 1.0.3 -m 'Fixing bug with list_app.CreateView.'
git push origin : 1.0.3
git checkout staging

git checkout master
git tag -a 1.0.4 -m 'Fixing bug with clipboard clear button. It deletes all cards/posts/lists now.'
git push origin : 1.0.4
git checkout staging

git checkout master
git tag -a 1.0.5 -m 'New shout mechanism implemented.'
git push origin : 1.0.5
git checkout staging


git checkout master
git tag -a 1.0.11 -m 'Bug fixes, getting to work with jsim.'
git push origin : 1.0.11
git checkout staging

git checkout master
git tag -a 1.1.0 -m 'Bug fixes, implementing undoing clipboard operations.'
git push origin : 1.1.0
git checkout staging

git checkout master
git tag -a 1.1.2 -m 'Improvement of colors and design.'
git push origin : 1.1.2
git checkout staging

git checkout master
git tag -a 1.2.0 
git push origin : 1.2.0
git checkout staging

##############################################################################
cd ~/projects/arcamens-code

# rename card_app to markdown_app.
grep -rl  'card_app' . | xargs sed -i 's/card_app/markdown_app/g' 
grep -rl  'Card' . | xargs sed -i 's/Card/Markdown/g' 
grep -rl  'card' . | xargs sed -i 's/card/markdown/g' 

##############################################################################
#fix #gitignore #remove #cached #files #ignore #folder #migrations

git rm -r --cached ./*/migrations/
git rm --cached db.sqlite3
git add .gitignore
##############################################################################

wget --post-data='somedata' http://189.84.248.176:8000/register_app/paypal-ipn/
##############################################################################
# install paybills in virtualenv.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/django-paybills-code
python setup.py install
rm -fr build
##############################################################################

# access victor server through ssh.

tee -i >(stdbuf -o 0 ssh arcamens@staging.arcamens.com 'bash -i')

# accept signals.
tee >(stdbuf -o 0 ssh arcamens@staging.arcamens.com 'bash -i')

# run as supervisord.
supervisord -n -c ../conf/supervisord.conf

# remove arcamens and paybills.
rm -fr /home/arcamens-test/projects/arcamens-code
rm -fr /home/arcamens-test/projects/django-paybills-code
##############################################################################
# install paybills
cd ~/projects/django-paybills-code
python setup.py install
##############################################################################
# passphrase for victor server.
bohju9Do

##############################################################################
# deploy arcamens on victor server.

cp -R ~/projects/arcamens-code /tmp
rm -fr /tmp/arcamens-code/.git
find /tmp/arcamens-code -path "arcamens-code/**/migrations/*.py" -not -name "__init__.py" -delete
find /tmp/arcamens-code -path "arcamens-code/**/migrations/*.pyc" -not -name "__init__.py" -delete
find /tmp/arcamens-code -path "arcamens-code*/*.pyc" -not -name "__init__.py" -delete
find /tmp/arcamens-code -name "db.sqlite3" -delete

# use rsync.
rsync -r /tmp/arcamens-code arcamens-test@job-lab.net:/home/arcamens-test/projects

# uses scp.
scp -r /tmp/arcamens-code arcamens-test@job-lab.net:/home/arcamens-test/projects

# remove the old code.
ssh arcamens-test@job-lab.net '
rm -fr /home/arcamens-test/projects/arcamens-code'

scp -r /home/tau/projects/arcamens-code/build-data opus@opus.test.splittask.net:/home/opus/projects/arcamens-code

##############################################################################
# install paybills on victor server.

cp -R ~/projects/django-paybills-code /tmp
rm -fr /tmp/django-paybills-code/.git

scp -r /tmp/django-paybills-code arcamens-test@job-lab.net:/home/arcamens-test/projects

ssh arcamens-test@job-lab.net '
cd ~/.virtualenvs/
source arcamens/bin/activate
cd /home/arcamens-test/projects/django-paybills-code
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
rm -fr arcamens
##############################################################################
# install blowdb
cd ~/projects/django-blowdb-code
python setup.py install
rm -fr build

##############################################################################
# check whether rabbitmq is running mqtt server on the port 
# for paho.
lsof -i tcp:1883

# check whether rabbitmq is running mqtt websocket server on the
# port for paho.

lsof -i tcp:15675
##############################################################################
# install rabbitmq mqqt plugin.

# Exchanges: messages sent to exchange get dispatched to the queues
# that are binded to it.
# rabbitmq-mqtt plugin has a default exchange amq.topic, consumers(ws clients)
# consume from queues binded to this exchange.
# the /ws thing is one default exchange for ws clients.
rabbitmq-plugins enable rabbitmq_web_mqtt

# https://www.rabbitmq.com/mqtt.html
# http://www.steves-internet-guide.com/into-mqtt-python-client/

# it explains the /ws.
# The /ws is an endpoint exposed by the plugin.
# https://www.rabbitmq.com/web-mqtt.html

# setting up rabbitmq to work on server.

tee -i >(stdbuf -o 0 ssh opus-test@staging.arcamens.com 'bash -i')

# first enable the management tool.
rabbitmq-plugins enable rabbitmq_management

# we can access from here:
# http://opus.test.splittask.net:15672/

# we need to create a test user
# then grant permissions to it on vhost /
# because mqtt plugin uses guest for default
# and guest is not allowed to access remotely the broker.

rabbitmqctl add_user test test
rabbitmqctl set_user_tags test administrator
rabbitmqctl set_permissions -p / test ".*" ".*" ".*"

# then we create the configuration file for setting up
# the user for the mqtt plugin.
# the web_mqtt plugin relies on mqtt plugin
# it is a dependency.
# we set the user as test/test.
echo '
[{rabbit,        [{tcp_listeners,    [5672]}]},
 {rabbitmq_mqtt, [{default_user,     <<"test">>},
                  {default_pass,     <<"test">>},
                  {allow_anonymous,  true},
                  {vhost,            <<"/">>},
                  {exchange,         <<"amq.topic">>},
                  {subscription_ttl, 1800000},
                  {prefetch,         10},
                  {ssl_listeners,    []},
                  %% Default MQTT with TLS port is 8883
                  %% {ssl_listeners,    [8883]}
                  {tcp_listeners,    [1883]},
                  {tcp_listen_options, [{backlog,   128},
                                        {nodelay,   true}]}]}].

' > /etc/rabbitmq/rabbitmq.config

# point the config file in the rabbitmq-env.conf
# it took me a shitload of time to understand
# that setting up the plugins should be done
# in the rabbitmq.config not in the rabbitmq-env.conf.
echo 'RABBITMQ_CONFIG_FILE=/etc/rabbitmq/rabbitmq
' > /etc/rabbitmq/rabbitmq-env.conf

rabbitmqctl stop
rabbitmqctl start&

# then we are done, it is enough to run the server.
##############################################################################
# run arcamens on victor server.

ssh root@staging.arcamens.com 'rabbitmq-server start;exit;'

# activate virtualenv on victor server.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/arcamens-code

# run arcamens project on victor server.
cd ~/projects/arcamens-code
stdbuf -o 0 python manage.py runserver 0.0.0.0:8000
##############################################################################
# stop arcamens running, kill the process.
ps aux | grep mana

##############################################################################
# install django-slock

cd ~/projects/django-slock-code
python setup.py install
rm -fr build
##############################################################################
# install django-jsim

cd ~/projects/django-jsim-code
python setup.py install
rm -fr build

##############################################################################

# install django-scrolls
cd ~/projects/django-scrolls-code
python setup.py install
rm -fr build
##############################################################################
# pair fork master branch to upstream master branch.
git fetch -p 
git checkout master
git reset --hard f7e9f0b  
git push origin master --force 

##############################################################################
# create C316 branch.
cd ~/projects/arcamens-code
git branch -a
git checkout -b C316
git push --set-upstream origin C316

##############################################################################
# merge C316 into staging.
git checkout staging
git merge C316
git push -u origin staging
##############################################################################
# delete C316 branch.
cd ~/projects/arcamens-code
git branch -d C316
git push origin :C316
git fetch -p 
##############################################################################
# fetch remote branch
git pull
git checkout C162
##############################################################################
# merge C162 into staging.
git checkout staging
git merge C162
git push -u origin staging

git branch -d C162
git push origin :C162
git fetch -p 
##############################################################################
# install django-sqlike

cd ~/projects/django-sqlike-code
python setup.py install
rm -fr build

##############################################################################
# Restart supervisor.

tee >(stdbuf -o 0 ssh root@staging.arcamens.com 'bash -i')
sudo supervisorctl restart arcamens
##############################################################################
# run migrations arcamens on victor vps as root.

tee >(stdbuf -o 0 ssh arcamens@staging.arcamens.com 'bash -i')

cd ~/.virtualenv/
source opus/bin/activate
cd ~/projects/arcamens-code
git pull 
git status
git log

# Do migrations.
python manage.py apps
python manage.py migrate

exit


# View uwsgi logs in victor server.
tail -f ../logs/uwsgi.log
##############################################################################
# install wsbells in virtualenv.
cd ~/.virtualenvs/
source opus/bin/activate

cd ~/projects/django-wsbells-code
python setup.py install
rm -fr build
##############################################################################
# install py-gfm github flavoured markdown.

pip install py-gfm

##############################################################################
# enable autoplay policy user gesture.

# In Chrome this seems to be working now, anno 2017: HTML5 videos play automatically in Chrome (59) on Android (7.1.1).
# 
# Note that the videos start muted. You can enable autoplay with sound on Android Chrome by navigating to chrome://flags and set gesture requirement for media playback to disabled (per this answer).
# 
# (Note that unfortunately disabling this flag seems to have no impact on an embedded YouTube video. I have openened a new question for this.)
##############################################################################
# bitbucket references.

# In my android it is autoplay policy.
# chrome://flags/#autoplay-policy t

# I decided NOT to use the following libraries, but to write from scratch:
# https://bitbucket.org/atlassian/python-bitbucket
# https://django-oauth-toolkit.readthedocs.io/en/latest/ (for servers?)
# https://github.com/requests/requests-oauthlib (https://github.com/requests/requests-oauthlib/blob/a116d06dbb69ea5eb4fbe46530af27b12ad6d82c/docs/oauth2_workflow.rst#refreshing-tokens)
##############################################################################
# access arcamens database.

mysql -u staging -p staging

password ueLa6eer
##############################################################################
# Fixing issue with migrations after renaming model bitbucket_app.

rm -fr app/migrations

# drop tables to solve the problem with unkonwn field in migrations.
ssh arcamens@staging.arcamens.com
mysql -i -u staging -p staging
ueLa6eer

DROP TABLE bitbucket_app_bitbuckethooker;    

DROP TABLE bitbucket_app_ebitbucketcommit;

# Delete the app migrations.

delete from django_migrations where app = 'bitbucket_app';

# Remove the old migrations.
rm -fr bitbucket_app/migrations

python manage.py makemigrations bitbucket_app
python manage.py migrate bitbucket_app 
##############################################################################
# backup of the db on victor server.

mysqldump -u staging -p staging > ../mysql.sql
##############################################################################

grep -rl '#smallModalContent' --exclude-dir='.git' ./ | xargs sed -i 's/#smallModalContent/#smallModalContent/g'

##############################################################################
DROP TABLE bitbucket_app_ebitbucketcommit;

delete from django_migrations where app = 'core_app';
delete from django_migrations where app = 'paybills';

DROP TABLE paybills_paymentprocess;
DROP TABLE paybills_paymentsuccess;
DROP TABLE paybills_service                 ;
DROP TABLE paybills_subscriptionpayment     ;
DROP TABLE paybills_subscriptionprocess     ;
DROP TABLE paybills_subscriptionsuccess     ;
DROP TABLE paybills_unsubscriptionsuccess ;
##############################################################################
# create missing column in mysql, fix issues with migrations.

alter table core_app_user add column max_users INT NULL DEFAULT 3;



