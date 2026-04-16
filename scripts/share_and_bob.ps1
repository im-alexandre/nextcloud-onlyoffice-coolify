$c = "nextcloud-onlyoffice-coolify-nextcloud-1"
docker exec -u www-data $c php occ files:scan --path="/admin/files" 2>&1
docker exec -u www-data $c php occ sharing:share --with=bob --type=0 --permissions=19 "/admin/files/Relatorio da equipe.docx" 2>&1
