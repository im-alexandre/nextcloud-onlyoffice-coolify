# Nextcloud + OnlyOffice — guia rápido para auto-hospedar

Este repositório sobe uma stack **Nextcloud + OnlyOffice Document Server** usando Docker Compose. O foco é ter algo funcionando em **localhost** em menos de 10 minutos para você experimentar antes de decidir se expõe publicamente.

> ⚠️ **Antes de qualquer uso real, troque todas as senhas e o segredo JWT** no `docker-compose.yml`: `POSTGRES_PASSWORD`, `NEXTCLOUD_ADMIN_PASSWORD` e `JWT_SECRET`.

## O que é

- **[Nextcloud](https://nextcloud.com/)** — um "Google Drive self-hosted": sincronização de arquivos, compartilhamento, calendário, contatos, colaboração.
- **[OnlyOffice Document Server](https://www.onlyoffice.com/)** — um editor de documentos (Word/Excel/PowerPoint) que roda no navegador, com colaboração em tempo real.
- Juntos: você clica num `.docx` dentro do Nextcloud e ele abre direto num editor dentro do próprio navegador, sem precisar do Microsoft Office.

## Conceitos em 2 minutos

```
Seu navegador
    │
    ├── http://localhost:8080 ──► Nextcloud (Apache)
    │                                 │
    │                                 ├── PostgreSQL (dados/metadados)
    │                                 └── Redis      (cache/locks)
    │
    └── http://localhost/    ──► OnlyOffice Document Server (nginx)
                                      ▲
                                      │ callbacks JWT
                                      ▼
                                  Nextcloud
```

- Nextcloud é quem guarda os arquivos e mostra a interface.
- OnlyOffice é um "serviço de edição" — quando você abre um documento, o Nextcloud embute o editor do OnlyOffice em um iframe.
- Os dois se autenticam mutuamente via **JWT** (um segredo compartilhado). Se os segredos dos dois lados não baterem, o editor não carrega.

## Pré-requisitos

1. **Docker** e **Docker Compose v2** instalados.
2. **Portas 80 e 8080 do host livres**. O OnlyOffice vai ocupar a 80 e o Nextcloud a 8080. Se você tem apache, nginx, caddy ou qualquer outra coisa usando essas portas, pare antes de subir a stack:
   ```bash
   ss -ltnp | grep -E ':80 |:8080 '
   ```
   Se retornar algo, mate esse processo.
3. **Docker Desktop (Mac/Windows)**: este compose usa `network_mode: host`, que só é suportado a partir do **Docker Desktop 4.29 (2024)** e precisa ser ligado manualmente em **Settings → Resources → Network → Enable host networking**. No Linux funciona sem ajuste.

## Subindo pela primeira vez

```bash
git clone https://github.com/im-alexandre/nextcloud-onlyoffice-coolify.git
cd nextcloud-onlyoffice-coolify

# EDITE o docker-compose.yml e troque TODAS as senhas e o JWT_SECRET antes.

docker compose up -d
docker compose logs -f nextcloud
```

Aguarde 1–2 minutos na primeira vez (o Nextcloud faz `occ install` sozinho). Quando os logs mostrarem `resuming normal operations`, abra:

- Nextcloud: http://localhost:8080
- OnlyOffice healthcheck: http://localhost/healthcheck (deve retornar `true`)

Login no Nextcloud: usuário/senha que você colocou em `NEXTCLOUD_ADMIN_USER` / `NEXTCLOUD_ADMIN_PASSWORD`. Você cai direto no dashboard, sem passar pelo wizard de instalação.

## Ativando o editor OnlyOffice no Nextcloud

1. Logado como admin, vá em **Apps** (ícone do seu avatar → Apps).
2. Busque por **ONLYOFFICE** e clique **Download and enable** (o connector oficial — versão v10 ou superior).
3. Vá em **Administration settings → ONLYOFFICE**.
4. Preencha:
   - **Document Editing Service address**: `http://localhost/`
   - **Secret key (leave blank to disable)**: o mesmo valor que você colocou em `JWT_SECRET` no `docker-compose.yml`.
5. Expanda **Advanced server settings** e preencha:
   - **Document Editing Service address for internal requests from the server**: `http://localhost/`
   - **Server address for internal requests from the Document Editing Service**: `http://localhost:8080/`
6. Clique **Save**. Se aparecer um erro vermelho, 99% das vezes é JWT errado ou porta bloqueada — veja a seção de troubleshooting.

Por que todos os endereços são `localhost`? Porque no compose simples todos os containers rodam em `network_mode: host`, ou seja, compartilham a stack de rede do host. Dentro de qualquer container, `localhost` = a sua máquina. Isso elimina a necessidade de `host.docker.internal` ou nomes de serviço Docker.

Pronto. Crie um documento novo: **Files → +** → **New Document (.docx)** → o editor abre em iframe.

## Gestão de usuários e grupos

Tudo pela UI do Nextcloud — sem precisar de CLI.

**Criar usuário**:
1. Avatar no topo direito → **Users**.
2. Clique **+ New user** no topo.
3. Preencha username, nome, senha inicial, email, grupos, quota (ex.: `5 GB`).
4. Salvar. O usuário já pode logar.

**Criar grupo**:
1. Na mesma tela de Users, sidebar esquerda → **Add group**.
2. Arraste usuários para o grupo, ou edite cada usuário e selecione o grupo.

**Mudar quota depois**: na tela de Users, clique na quota do usuário e escolha outra (ou digite um valor custom).

**Tornar usuário administrador**: na criação ou edição, adicione-o ao grupo `admin`.

## Compartilhamento e permissões

Todo arquivo ou pasta tem um botão de **share** (ícone ao lado do nome).

- **Share com usuário interno**: comece a digitar o nome — ele aparece. Permissões: read, edit, create, delete, reshare.
- **Share com grupo**: mesma coisa, só que digitando o nome do grupo.
- **Link público**: toggle "Share link" → ele gera uma URL. No menu `...` ao lado você pode:
  - Adicionar senha.
  - Definir data de expiração.
  - Tornar read-only, file drop (só upload), ou hide download.
- **Federated share**: compartilhar com alguém de outro Nextcloud via `usuario@servidor.com`.

Boas práticas:
- Use **grupos** em vez de compartilhar individualmente com cada pessoa.
- Links públicos sempre com senha e expiração.
- Permissões mínimas necessárias — prefira read-only se a pessoa só precisa ler.

## Backup

Pare a stack antes de fazer backup para garantir consistência:

```bash
docker compose down
```

Para cada volume importante, rode:

```bash
docker run --rm \
  -v nextcloud-onlyoffice-coolify_db_data:/data \
  -v "$PWD":/backup alpine \
  tar czf /backup/db_data.tgz -C /data .

docker run --rm \
  -v nextcloud-onlyoffice-coolify_nextcloud_data:/data \
  -v "$PWD":/backup alpine \
  tar czf /backup/nextcloud_data.tgz -C /data .

docker run --rm \
  -v nextcloud-onlyoffice-coolify_onlyoffice_data:/data \
  -v "$PWD":/backup alpine \
  tar czf /backup/onlyoffice_data.tgz -C /data .
```

> Os nomes reais dos volumes são `<nome-da-pasta>_<volume>`. Confira com `docker volume ls`.

Suba a stack de novo:

```bash
docker compose up -d
```

**Restore**: pare a stack, crie os volumes vazios, e inverta o `tar`:

```bash
docker run --rm \
  -v nextcloud-onlyoffice-coolify_db_data:/data \
  -v "$PWD":/backup alpine \
  sh -c "cd /data && tar xzf /backup/db_data.tgz"
```

Repita para cada volume e suba a stack.

## Atualização dos containers

```bash
docker compose pull
docker compose up -d
```

O Nextcloud roda `occ upgrade` automaticamente no startup. **Importante**: não pule majors — se a imagem pinada aqui é a 33 e sai a 34, tudo bem subir. Mas se você deixou a stack parada por muito tempo e vai de 33 → 36, suba intermediários antes (33 → 34 → 35 → 36), cada um com `docker compose up -d` e espera do `occ upgrade` completar.

Antes de qualquer atualização, **faça backup**.

## Para rodar em produção

O compose localhost deste repo é só para brincar. Para uso real você precisa de:

- HTTPS de verdade (Let's Encrypt ou equivalente).
- Um proxy reverso (Caddy, Traefik, nginx).
- Domínio público em `NEXTCLOUD_TRUSTED_DOMAINS`, `OVERWRITEHOST`, `OVERWRITEPROTOCOL`.
- Senhas rotacionadas e armazenadas fora do compose (secrets, `.env` não commitado, etc.).
- Backups automáticos.

Como exemplo concreto, veja o [`docker-compose-coolify.yml`](./docker-compose-coolify.yml) neste repo — é um deploy real rodando no [Coolify](https://coolify.io/) com Traefik e TLS para os domínios `cloud.drg.ink` e `docs.drg.ink`. Ele ilustra labels Traefik, headers de segurança HSTS, CA interna montada nos containers e uso de rede Docker externa.

## Troubleshooting

### "Error while downloading the document file" ou o editor não carrega

Quase sempre é **JWT mismatch**. Confira que o valor de `JWT_SECRET` no `docker-compose.yml` é **exatamente** o mesmo que você colou em **Secret key** na configuração do connector ONLYOFFICE no Nextcloud. Sem espaços extras, sem aspas.

Outra causa: porta 80 bloqueada. Teste `curl http://localhost/healthcheck` — tem que retornar `true`. Se não, o OnlyOffice não subiu — cheque `docker compose logs onlyoffice`.

### "Access through untrusted domain"

Você está acessando por um hostname que não é `localhost`. Duas opções:

1. Adicione o hostname em `NEXTCLOUD_TRUSTED_DOMAINS` no compose, separado por espaço, e rode `docker compose up -d` de novo.
2. Ou, com a stack rodando:
   ```bash
   docker compose exec --user www-data nextcloud \
     php occ config:system:set trusted_domains 1 --value=meu.dominio.local
   ```

### Upload de arquivo grande falha

Aumente os limites PHP no serviço `nextcloud` do compose:

```yaml
PHP_UPLOAD_LIMIT: 2048M
PHP_MEMORY_LIMIT: 2048M
```

Reinicie: `docker compose up -d`.

### Porta 80 já em uso no host

```bash
ss -ltnp | grep ':80 '
```

Pare o processo que aparecer (apache2, nginx, caddy, etc.) ou mude o compose para não usar host networking — mas aí você perde a conveniência de ter só URLs `localhost` no connector.
