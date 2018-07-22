##############################################################################
# push arcamens staging branch.
cd ~/projects/arcamens-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;
rm -fr ~/projects/arcamens-code/static/media
git status
git add *
git commit -a
git push -u origin staging
#############################################################################
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
# merge alpha into staging.
git checkout staging
git merge alpha
git push -u origin staging
git checkout staging

git branch -d alpha
git push origin :alpha
git fetch -p 

##############################################################################
cd ~/projects/arcamens-code
git pull
##############################################################################
# erase database.
cd ~/projects/arcamens-code
python manage.py blowdb
./build-data

python manage.py makemigrations
python manage.py migrate
##############################################################################
# stress-db.
./stress-db teta 1
##############################################################################
# create alpha branch.
git checkout -b alpha
git push --set-upstream origin alpha
##############################################################################
# switch to alpha branch.
git checkout alpha
##############################################################################
# run arcamens project.
cd ~/projects/arcamens-code
stdbuf -o 0 python manage.py runserver 0.0.0.0:8000
#####k#########################################################################
# create arcamens virtualenv.
cd ~/.virtualenvs/
ls -la
# by default, python3 has executable named python in arch linux.
virtualenv arcamens -p /usr/bin/python
##############################################################################
# activate arcamens virtualenv.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/arcamens-code
##############################################################################
# install arcamens dependencies virtualenv.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/arcamens-code
pip install -r debug.requirements.txt 
##############################################################################
# create arcamens project.
cd ~/projects/
django-admin startproject arcamens arcamens-code
##############################################################################
# create core_app app.
cd ~/projects/arcamens-code
python manage.py startapp core_app
##############################################################################
# create onesignal app.
cd ~/projects/arcamens-code
python manage.py startapp onesignal
##############################################################################
# create timeline app.
cd ~/projects/arcamens-code
python manage.py startapp post_app
##############################################################################
# create comment_app app.
cd ~/projects/arcamens-code
python manage.py startapp comment_app

##############################################################################
# create timeline_app app.
cd ~/projects/arcamens-code
python manage.py startapp timeline_app
##############################################################################
# create stream app.
cd ~/projects/arcamens-code
python manage.py startapp stream_app
##############################################################################
# delete last commit.

cd ~/projects/arcamens-code
git reset HEAD^ --hard
git push -f
##############################################################################
# install paybills in virtualenv.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/django-paybills-code
python setup.py install
rm -fr build
##############################################################################
# access victor server through ssh.

tee -i >(stdbuf -o 0 ssh ssh admin@staging.arcamens.com 'bash -i')
##############################################################################
# run supervisord.
supervisord -n -c ../conf/supervisord.conf

##############################################################################
# deploy arcamens on victor server.
# use rsync.
rsync -r folder arcamens-test@job-lab.net:/path/

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

tee -i >(stdbuf -o 0 ssh admin@staging.arcamens.com 'bash -i')

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
# install django-jscroll-code
cd ~/projects/django-jscroll-code
python setup.py install
rm -fr build
##############################################################################
# install onesignal.
cd ~/projects/django-onesignal-code
python setup.py install
rm -fr build

##############################################################################
# pair fork master branch to upstream master branch.
git fetch -p 
git checkout master
git reset --hard f7e9f0b  
git push origin master --force 

##############################################################################
# install django-sqlike

cd ~/projects/django-sqlike-code
python setup.py install
rm -fr build

##############################################################################
# Restart supervisor.

tee >(stdbuf -o 0 ssh admin@staging.arcamens.com 'bash -i')
sudo supervisorctl restart arcamens
sudo supervisorctl stop arcamens

##############################################################################
# View uwsgi logs in victor server.
tail -f ../logs/uwsgi.log
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
tee >(stdbuf -o 0 ssh arcamens@staging.arcamens.com 'bash -i')

mysql -u staging -p staging

password Ighaw5aaquaeph5H
##############################################################################
# access arcamens staging.
tee >(stdbuf -o 0 ssh staging@staging.arcamens.com 'bash -i')

tee >(stdbuf -o 0 mysql -u staging -p staging)
Ighaw5aaquaeph5H
##############################################################################
# Fixing issue with migrations after renaming model bitbucket_app.

rm -fr app/migrations

# drop tables to solve the problem with unkonwn field in migrations.

mysql -i -u staging -p staging
Ighaw5aaquaeph5H

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
# bind user to all boards/timelines joinall command.

python manage.py restore_ownership port arca ioli
##############################################################################
# Drop project tables and recreate it.

DROP DATABASE staging;
CREATE DATABASE staging;
##############################################################################
# dump db as json and restore it.

python manage.py dumpdata --exclude auth.permission --exclude contenttypes > arcamens-db.json

python manage.py loaddata arcamens-db.json
##############################################################################
pip install html2text
##############################################################################
# install django-listutils-code
cd ~/projects/django-listutils-code
python setup.py install
rm -fr build

python manage.py normalize_events
##############################################################################
# compile docs.

cd ~/projects/arcamens-code/site_app/static/site_app/help
pandoc --toc -s index.md -o index.html

##############################################################################
# site password.

user arcamens
password LQ3Q38hg7F94
##############################################################################
# first deploy on staging.

# create the user.
sudo adduser staging -u bash
mkdir ~/projects/
mkdir ~/.virtualenvs/

# add deploy key.
cp -i ~arcamens/.ssh/id_rsa.pub ~staging/.ssh/id_rsa.pub
cp `~/.ssh/id_rsa`  `~/.ssh/id_rsa.pub`

# open supervisord.conf and replace all arcamens -> staging
# except arcamens-code

grep -rl --exclude-dir='.git' 'Timeline' ./ | xargs sed -i 's/Timeline/Group/g'
grep -rl --exclude-dir='.git' 'timeline' ./ | xargs sed -i 's/timeline/group/g'

sed -i 's/Timeline/Group/g' arcamens-db.json

sed -i 's/timeline/group/g' arcamens-db.json
##############################################################################
# Approach for renaming django app with existing db.

# Make a backup of the db as json.
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > arcamens-db.json

sed -i 's/appname/newappname/g' arcamens-db.json
sed -i 's/appname/newappname/g' arcamens-db.json

# Switch to the commit that has the app renamed then restore the db.
# The idea consists of renaming the occurrences of the app. it works in some
# cases though.
python manage.py loaddata arcamens-db.json

python manage.py dumpdata --exclude auth.permission --exclude contenttypes > arcamens-db.json

#############################################################################
# push arcamens beta branch.
cd ~/projects/arcamens-code
# clean up all .pyc files. 
find . -name "*.pyc" -exec rm -f {} \;
rm -fr ~/projects/arcamens-code/static/media
git status
git add *
git commit -a
git push -u origin beta
##############################################################################
# create beta branch.
git checkout -b beta
git push --set-upstream origin beta
##############################################################################
# reset c_storage, c_download all counters.
python manage.py reset_counters

