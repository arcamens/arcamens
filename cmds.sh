cp -R ~/projects/django-paybills-code /tmp
rm -fr /tmp/django-paybills-code/.git

scp -r /tmp/django-paybills-code opus-test@job-lab.net:/home/opus-test 
ssh opus-test@job-lab.net '
cd /home/opus-test/django-paybills-code
sudo python setup.py install'




cp -R ~/projects/opus-code /tmp
rm -fr /tmp/opus-code/.git
find /tmp/opus-code -path "opus-code*/migrations/*.py" -not -name "__init__.py" -delete
find /tmp/opus-code -path "opus-code*/migrations/*.pyc" -not -name "__init__.py" -delete
find /tmp/opus-code -path "opus-code*/*.pyc" -not -name "__init__.py" -delete
find /tmp/opus-code -name "db.sqlite3" -delete

scp -r /tmp/opus-code opus-test@job-lab.net:/home/opus-test

rsync -r /tmp/opus-code opus-test@job-lab.net:/home/opus-test

ssh opus-test@job-lab.net '
rm -fr /home/opus-test/opus-code'

tee -i >(stdbuf -o 0 ssh opus-test@job-lab.net 'bash -i')

cd /home/opus-test/

