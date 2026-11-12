# Develop locally

The whole stack runs on your machine in Docker Compose, driven by the
[`Makefile`](https://github.com/suitenumerique/drive/blob/main/Makefile). How a
change gets reviewed and merged is in
[`CONTRIBUTING.md`](https://github.com/suitenumerique/drive/blob/main/CONTRIBUTING.md).

## TL;DR

```bash
# 1. Get the code; to propose a change, clone your fork instead
git clone https://github.com/suitenumerique/drive.git && cd drive
# 2. Build the images, create the database, start the stack
make bootstrap
# 3. Open http://localhost:3000 and sign in as drive / drive
# 4. Run the backend tests, then format and lint the backend
make test && make lint
# 5. Stop the stack, keeping its data
make stop
```

## Prerequisites

| Tool | What it is for |
| --- | --- |
| Git | Cloning the repository and committing |
| Docker Engine with the Compose plugin | Every service of the stack. The `Makefile` calls `docker compose`, never the old `docker-compose` |
| GNU Make | The `make` targets on this page |
| Node.js 22 to 24 and Yarn 1.22 | Every `make` target that runs `yarn` on your machine: the frontend outside its container, `make frontend-lint` and the end-to-end tests. The range is the [`engines` field](https://github.com/suitenumerique/drive/blob/main/src/frontend/package.json#L8-L11) of the frontend |

The first `make bootstrap` downloads and builds many gigabytes of images, and the
storage container answers `Disk full` as a server error when the disk fills.
Check the free space with `df -h /` first.

## Start the stack

```bash
make bootstrap
```

It builds the backend and frontend images, creates the database, compiles the
backend translations and the email templates, then starts everything. Run it again
after pulling changes, so new dependencies and migrations are applied.

### Where everything answers

| Service | Address | Login |
| --- | --- | --- |
| Drive | <http://localhost:3000> | `drive` / `drive`, or `paige`, `miles`, `archie`, `mark` with password `pass`: the users of [`docker/auth/realm.json`](https://github.com/suitenumerique/drive/blob/main/docker/auth/realm.json) |
| Backend API | <http://localhost:8071/api/v1.0/> | The browser session from signing in to Drive |
| Django admin | <http://localhost:8071/admin/> | `admin@example.com` / `admin`, created by `make superuser` |
| Keycloak | <http://localhost:8083>, behind the `nginx` container | `admin` / `admin` for the administration console |
| RustFS, the S3 storage | <http://localhost:9000>, web console on <http://localhost:9001> | Access key `drive`, secret `password` |
| Mailcatcher | <http://localhost:1081>, every email the backend sends | None |
| Collabora | <http://localhost:9980> | `drive` / `password` |
| OnlyOffice | <http://localhost:9981> | None |
| PostgreSQL | `localhost:6434`, database `drive` | `dinum` / `pass` |

Every port in that table must be free, and so must 6379 for Redis, 6433 for
Keycloak's own database and 8080 for Keycloak itself.

### Everyday commands

| Command | What it does |
| --- | --- |
| `make run` | Starts the backend, its services and the frontend container. Run it after `make stop`, and after editing a file in `env.d/development/` |
| `make run-backend` | Starts everything except the frontend container, for when the frontend runs on your machine |
| `make stop` | Stops every container and keeps them, so the database survives until the next `make run` |
| `make down` | Removes the containers and their networks, and deletes the database files under `data/` |
| `make status` | Lists the containers and their state |
| `make logs` | Follows the Django server's log. For another service, run `docker compose logs -f <service>` |
| `make superuser` | Creates the Django admin `admin@example.com` with password `admin` |
| `make migrate` | Applies the database migrations |
| `make shell` | Opens a Django shell |
| `make help` | Lists every target with its description |

Your own settings go in `env.d/development/common.local`, which `make
bootstrap` creates and git ignores. A value there overrides the one in
`env.d/development/common`.

## Run the frontend on your machine

The frontend container rebuilds slowly. For frontend work, run it on your
machine with hot reload:

```bash
make frontend-development-install
make run-frontend-development
```

It stops the `frontend-dev` container first, then answers on the same
<http://localhost:3000>.

## Tests and linters

| Command | What it runs |
| --- | --- |
| `make test` | The backend test suite, in parallel |
| `make test-back` | The same suite in one process. Arguments after the target go to pytest |
| `make lint` | Formats and fixes the backend with Ruff, then runs pylint on the files changed since `origin/main` |
| `make frontend-lint` | The frontend linter |

The end-to-end tests drive a browser with Playwright against a backend that
runs on its own database:

```bash
# Once: the end-to-end database and the frontend dependencies
make bootstrap-e2e
# Once: the browsers
cd src/frontend/apps/e2e && yarn install-playwright && cd -
# The backend on the end-to-end database, and the frontend
make run-backend-e2e run-frontend-development
# In a second terminal: the file picker's test page
make build-frontend-sdk run-frontend-sdk-development
# In a third terminal: the tests
make run-tests-e2e
```

## Next steps

- [Test on a phone](local-network.md) makes the stack reachable from another
  device on your network.
- [Check performance](scaling.md) fills the database with a production-sized
  dataset and profiles a change against it.
