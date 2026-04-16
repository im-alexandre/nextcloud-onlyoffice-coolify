$c = "nextcloud-onlyoffice-coolify-nextcloud-1"

# Instala o app ONLYOFFICE connector
docker exec -u www-data $c php occ app:install onlyoffice 2>&1

# Configura URLs e JWT
# Browser → OnlyOffice (porta 80 mapeada no host)
docker exec -u www-data $c php occ config:app:set onlyoffice DocumentServerUrl --value="http://localhost/" 2>&1

# Nextcloud container → OnlyOffice container (rede bridge Docker)
docker exec -u www-data $c php occ config:app:set onlyoffice DocumentServerInternalUrl --value="http://onlyoffice/" 2>&1

# OnlyOffice container → Nextcloud container (rede bridge Docker)
docker exec -u www-data $c php occ config:app:set onlyoffice StorageUrl --value="http://nextcloud/" 2>&1

# JWT
docker exec -u www-data $c php occ config:app:set onlyoffice jwt_secret --value="troque_este_segredo_jwt_bem_grande" 2>&1
docker exec -u www-data $c php occ config:app:set onlyoffice jwt_header --value="Authorization" 2>&1

# Verifica
docker exec -u www-data $c php occ config:app:get onlyoffice DocumentServerUrl 2>&1
docker exec -u www-data $c php occ config:app:get onlyoffice DocumentServerInternalUrl 2>&1
docker exec -u www-data $c php occ config:app:get onlyoffice StorageUrl 2>&1
docker exec -u www-data $c php occ config:app:get onlyoffice jwt_secret 2>&1
