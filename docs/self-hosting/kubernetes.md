# Install on Kubernetes

For administrators installing Drive with its Helm chart. The guide first runs
everything on a test cluster on your machine, then lists what to replace for
production.

The chart deploys Drive's backend, frontend, Celery workers and Celery beat,
and the jobs that migrate the database. PostgreSQL, Redis, the S3 bucket and the
sign-in provider are yours to provide: this guide installs throwaway ones from
[`helm-dev-backend`](https://github.com/suitenumerique/helm-dev-backend), a
chart for development only.

## TL;DR

```bash
# 1. A local cluster with ingress-nginx and certificates for *.127.0.0.1.nip.io
./bin/start-kind.sh && kubectl config set-context --current --namespace=drive
# 2. Keycloak, Redis, PostgreSQL and MinIO, for testing only
R=https://suitenumerique.github.io/helm-dev-backend
for s in keycloak redis postgresql minio; do helm install --repo $R -f docs/examples/helm/$s.values.yaml $s dev-backend; done
# 3. Drive itself
helm repo add drive https://suitenumerique.github.io/drive/
helm install drive drive/drive -f docs/examples/helm/drive.values.yaml
# 4. Open https://drive.127.0.0.1.nip.io and sign in as drive / drive
```

## Prerequisites

| Tool | What for |
| --- | --- |
| [Docker](https://docs.docker.com/get-started/get-docker/) | Running the test cluster |
| [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) | Creating the test cluster |
| [mkcert](https://github.com/FiloSottile/mkcert#installation) | Certificates your browser trusts for the test domains |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) and [Helm](https://helm.sh/docs/intro/install/) | Installing the charts |

Run every command from a clone of the
[repository](https://github.com/suitenumerique/drive): the values files are in
[`docs/examples/helm/`](https://github.com/suitenumerique/drive/tree/main/docs/examples/helm).

## 1. Create a test cluster

```bash
./bin/start-kind.sh
kubectl config set-context --current --namespace=drive
```

[`bin/start-kind.sh`](https://github.com/suitenumerique/drive/blob/main/bin/start-kind.sh)
creates a cluster named `suite` and installs ingress-nginx with a certificate
for `*.127.0.0.1.nip.io`. Every name under that domain points to your machine,
and to ingress-nginx inside the cluster, so the guide's addresses work with no
DNS to set up. It also creates the `drive` namespace and, in it, a `certifi`
ConfigMap: a certificate bundle including mkcert's root, which the Drive values
file mounts so the backend trusts Keycloak's and MinIO's certificates. The
cluster is ready once `kubectl -n ingress-nginx get pods` shows the controller
`Running`.

## 2. Install the services Drive needs

Each command installs one service from the development chart, configured by a
values file of the repository:

```bash
R=https://suitenumerique.github.io/helm-dev-backend
helm install --repo $R -f docs/examples/helm/keycloak.values.yaml keycloak dev-backend
helm install --repo $R -f docs/examples/helm/redis.values.yaml redis dev-backend
helm install --repo $R -f docs/examples/helm/postgresql.values.yaml postgresql dev-backend
helm install --repo $R -f docs/examples/helm/minio.values.yaml minio dev-backend
```

They are ready once `kubectl get pods` shows the four `Running`. The
[Drive values file](https://github.com/suitenumerique/drive/blob/main/docs/examples/helm/drive.values.yaml)
already points to them by the names these releases give them, such as
`redis-dev-backend-redis` for Redis.

## 3. Install Drive

```bash
helm repo add drive https://suitenumerique.github.io/drive/
helm install drive drive/drive -f docs/examples/helm/drive.values.yaml
```

`kubectl get pods` then shows the backend, the frontend, a Celery worker and
Celery beat `Running`. The `migrate`, `createsuperuser` and `configure-wopi`
jobs show `Completed` for 30 seconds, then the chart removes them.

## 4. Check it works

Open <https://drive.127.0.0.1.nip.io> and sign in as `drive` with the password
`drive`, the user the Keycloak values file creates. Upload a file, then open
it: the upload proves the browser reaches the bucket, and the preview proves
the download path through ingress-nginx.

The Django admin answers on <https://drive.127.0.0.1.nip.io/admin/>, as
`admin@example.com` with the password `admin`.

## Go to production

The test setup trades safety for speed. For production, replace each piece:

- **The services.** Point `backend.envVars` at your own PostgreSQL, Redis and
  S3 bucket, with the variables of
  [Start here](../reference/env-variables.md#start-here). Browsers upload to
  the bucket directly, so it needs a CORS rule allowing your Drive domain:
  `python manage.py bucket_cors --set`, in a backend pod, writes one allowing
  `https://` on every host of `DJANGO_ALLOWED_HOSTS`, plus the pod's own
  address.
- **The secrets.** Read them from Kubernetes secrets, as the example does for
  the database: `secretKeyRef` with the secret's `name` and `key`.
- **The sign-in provider.** Register Drive with yours, as
  [Sign-in](configuration/authentication.md) explains.
- **The certificates.** Drop the `certifi` volume once your services carry
  certificates from a public authority.
- **Email.** Point `DJANGO_EMAIL_HOST` at a real mail server: the test setup
  has none, so Drive only logs the emails it could not send.
- **The configuration.** `DJANGO_CONFIGURATION: Production`, a long random
  `DJANGO_SECRET_KEY`, and an SMTP server for invitations.
- **The images.** Pin `image.tag` and `frontend.image.tag` to a release
  instead of `latest`.

Every value the chart takes is in its
[`values.yaml`](https://github.com/suitenumerique/drive/blob/main/src/helm/drive/values.yaml).
The media ingresses check each download with Drive before the bucket answers,
through ingress-nginx's `auth-url` annotation, so the cluster needs
ingress-nginx.
