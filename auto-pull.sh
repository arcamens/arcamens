ssh root@staging.arcamens.com  <<'ENDSSH'
su arcamens
cd ~/projects/arcamens
git pull | echo "Upgrading"
exit
sudo supervisorctl restart arcamens

ENDSSH


