$c = "nextcloud-onlyoffice-coolify-nextcloud-1"

# Adiciona hostnames de container aos trusted_domains
docker exec -u www-data $c php occ config:system:set trusted_domains 1 --value="nextcloud" 2>&1
docker exec -u www-data $c php occ config:system:set trusted_domains 2 --value="onlyoffice" 2>&1

# Desliga verificação de allow_local_remote_servers para callback interno
docker exec -u www-data $c php occ config:system:set allow_local_remote_servers --value=true --type=boolean 2>&1

# Verifica
docker exec -u www-data $c php occ config:system:get trusted_domains 2>&1
