# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Docker Compose stack that deploys **Nextcloud** (file storage/collaboration) + **OnlyOffice Document Server** (browser-based office editing) on a **Coolify**-managed server, with **Traefik** as the reverse proxy and **Let's Encrypt / internal CA** for TLS.

## Stack Architecture

```
Internet → Traefik (coolify network)
               ├── cloud.drg.ink  → nextcloud:80  (nextcloud:29-apache)
               └── docs.drg.ink   → onlyoffice:80 (onlyoffice/documentserver)

nextcloud ──┬── db      (postgres:16-alpine)   persisted in db_data volume
            └── redis   (redis:7-alpine)        persisted in redis_data volume
```

All services share the external Docker network `coolify`, which is managed by Coolify/Traefik. No service exposes ports directly to the host — routing is entirely through Traefik labels.

## Key Configuration Points

- **Passwords to change before deploying**: `POSTGRES_PASSWORD` (used in both `db` and `nextcloud` services), `NEXTCLOUD_ADMIN_USER`, `NEXTCLOUD_ADMIN_PASSWORD`.
- **Domains**: hardcoded as `cloud.drg.ink` (Nextcloud) and `docs.drg.ink` (OnlyOffice). Change in Traefik labels and Nextcloud env vars.
- **TLS**: uses a self-signed Coolify CA mounted at `/data/coolify/ssl/coolify-ca.crt` into both Nextcloud and OnlyOffice containers so they can trust each other over HTTPS internally.
- **OnlyOffice JWT**: currently disabled (`JWT_ENABLED: "false"`). To enable, uncomment `JWT_SECRET` and `JWT_HEADER` and configure the matching secret in the Nextcloud OnlyOffice connector app.

## Deployment

This compose file is intended to be imported directly into Coolify as a "Docker Compose" service. Coolify manages the `coolify` network and Traefik — do not add a Traefik service here.

After first boot, remove or comment out the `NEXTCLOUD_ADMIN_USER` and `NEXTCLOUD_ADMIN_PASSWORD` env vars so they aren't re-applied on container restart.
