ssh root@staging.arcamens.com  <<'ENDSSH'
su arcamens
cd ~/projects/arcamens-code
git commit -m 'Upgrading.'
git pull | echo "Upgrading"
exit
sudo supervisorctl restart arcamens

ENDSSH







