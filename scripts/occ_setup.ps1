$c = "nextcloud-onlyoffice-coolify-nextcloud-1"
docker exec -u www-data $c php occ group:add equipe 2>&1
docker exec -u www-data -e OC_PASS=senhaBob123! $c php occ user:add --password-from-env --display-name "Bob Silva" --group equipe bob 2>&1
docker exec -u www-data $c php occ user:list 2>&1
docker exec -u www-data $c php occ group:list 2>&1
