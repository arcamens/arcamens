ssh root@staging.arcamens.com  <<'ENDSSH'
su arcamens
cd ~/projects/arcamens
git commit -m 'Upgrading.'
git pull | echo "Upgrading"
exit
sudo supervisorctl restart arcamens

ENDSSH



