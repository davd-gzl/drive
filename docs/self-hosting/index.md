# Self-hosting

For system administrators running Drive for their organisation. Drive is a
backend, a frontend and background workers, which rely on services you provide.
[How Drive works](../overview/how-drive-works.md) describes each piece.

!!! tip "Supported: Kubernetes"

    The maintainers run Drive on Kubernetes with the Helm chart, and it is the
    install they document.

    [Install on Kubernetes](kubernetes.md){ .md-button .md-button--primary }

## What Drive needs

Drive does not ship these services, so your install provides each one:

| Service | What for |
| --- | --- |
| PostgreSQL | Files' names, folders, sharing and users |
| Redis | Sessions, the cache and the background tasks' queue |
| An S3-compatible bucket | The files themselves |
| An [OpenID Connect](https://openid.net/developers/how-connect-works/) provider | Signing users in, see [Sign-in](configuration/authentication.md) |
| An SMTP server | Emails sent when a file is shared |
| ingress-nginx, on Kubernetes | Checking each download's rights before the file leaves the bucket |

These are optional, and Drive works without them:

- [Collabora or OnlyOffice](configuration/online-editing.md), to edit
  documents in the browser.
- [A malware scanner](configuration/malware-detection.md), to scan uploads.
- [Find](configuration/search.md), to search inside files.

## Configure it

Every setting is an environment variable of the backend:
[Environment variables](../reference/env-variables.md) lists them all, the few
a new install must set first at the top.

| To | Read |
| --- | --- |
| Connect your sign-in provider | [Sign-in](configuration/authentication.md) |
| Let users edit documents online | [Online editing](configuration/online-editing.md) |
| Scan uploads for malware | [Malware detection](configuration/malware-detection.md) |
| Search inside files | [Full-text search](configuration/search.md) |
| Limit each user's storage | [Storage quotas](configuration/quotas.md) |
| Encrypt files in the bucket | [Encrypted storage](configuration/encryption.md) |
| Change colours, the footer and links | [Look and feel](configuration/theming.md) |
| Watch it with Prometheus | [Monitoring](configuration/monitoring.md) |
| Merge two accounts of one person | [Merging accounts](configuration/account-merging.md) |

## Upgrade it

Upgrade through every minor and major version in turn, fix releases aside,
and run the database migrations, `python manage.py migrate`, after each. What
each version changes for an administrator is in
[`UPGRADE.md`](https://github.com/suitenumerique/drive/blob/main/UPGRADE.md).

## Other ways to run it

The Docker images are `lasuite/drive-backend` and `lasuite/drive-frontend` on
[Docker Hub](https://hub.docker.com/u/lasuite). The repository also holds what
a [Scalingo](https://scalingo.com/) app needs, a
[`Procfile`](https://github.com/suitenumerique/drive/blob/main/Procfile)
and its scripts in [`bin/`](https://github.com/suitenumerique/drive/tree/main/bin),
without a guide. The Docker Compose stack of the repository is for development
only: [Develop locally](../contributing/develop.md) runs it.
