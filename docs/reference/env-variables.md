# Environment variables

Every environment variable the Drive backend reads, grouped by feature, with
its default and its meaning. The backend image, its Celery worker and its
Celery beat all read the same variables: on Kubernetes they go in
`backend.envVars` of the Helm chart.

Three formats recur:

- A list is comma-separated: `drive.example.com,www.drive.example.com`.
- A dictionary is a Python literal, so its booleans are `True` and `False`, not
  JSON's `true` and `false`: `{"SupportsRename": False}`.
- A secret can be read from a file: set `<NAME>_FILE` to the file's path and it
  wins over `<NAME>`. It works for the variables marked *file* below.

## Start here

Set these on a production backend. Without them it does not start, no one can
sign in, files cannot be downloaded, or no email is sent:

| Variable | What to set |
| --- | --- |
| [`DJANGO_CONFIGURATION`](#DJANGO_CONFIGURATION) | `Production` |
| [`DJANGO_SECRET_KEY`](#DJANGO_SECRET_KEY) | A long random string |
| [`DJANGO_ALLOWED_HOSTS`](#DJANGO_ALLOWED_HOSTS) | Drive's domain |
| [`DB_HOST`](#DB_HOST), [`DB_NAME`](#DB_NAME), [`DB_USER`](#DB_USER), [`DB_PASSWORD`](#DB_PASSWORD) | The PostgreSQL database, or one [`DATABASE_URL`](#DATABASE_URL) |
| [`REDIS_URL`](#REDIS_URL), [`DJANGO_CELERY_BROKER_URL`](#DJANGO_CELERY_BROKER_URL) | The Redis server |
| [`AWS_S3_ENDPOINT_URL`](#AWS_S3_ENDPOINT_URL), [`AWS_S3_ACCESS_KEY_ID`](#AWS_S3_ACCESS_KEY_ID), [`AWS_S3_SECRET_ACCESS_KEY`](#AWS_S3_SECRET_ACCESS_KEY), [`AWS_STORAGE_BUCKET_NAME`](#AWS_STORAGE_BUCKET_NAME) | The S3 bucket holding the files |
| [`MEDIA_BASE_URL`](#MEDIA_BASE_URL) | Drive's address, where browsers download files |
| [`OIDC_OP_AUTHORIZATION_ENDPOINT`](#OIDC_OP_AUTHORIZATION_ENDPOINT), [`OIDC_OP_TOKEN_ENDPOINT`](#OIDC_OP_TOKEN_ENDPOINT), [`OIDC_OP_USER_ENDPOINT`](#OIDC_OP_USER_ENDPOINT), [`OIDC_OP_JWKS_ENDPOINT`](#OIDC_OP_JWKS_ENDPOINT), [`OIDC_OP_LOGOUT_ENDPOINT`](#OIDC_OP_LOGOUT_ENDPOINT) | The sign-in provider's addresses |
| [`OIDC_RP_CLIENT_ID`](#OIDC_RP_CLIENT_ID), [`OIDC_RP_CLIENT_SECRET`](#OIDC_RP_CLIENT_SECRET) | Drive's client at that provider |
| [`LOGIN_REDIRECT_URL`](#LOGIN_REDIRECT_URL), [`LOGOUT_REDIRECT_URL`](#LOGOUT_REDIRECT_URL) | Drive's address |
| [`DJANGO_EMAIL_HOST`](#DJANGO_EMAIL_HOST), [`DJANGO_EMAIL_FROM`](#DJANGO_EMAIL_FROM), [`DJANGO_EMAIL_URL_APP`](#DJANGO_EMAIL_URL_APP) | The mail server, for share invitations |

Everything else has a working default. These features stay off until they are
set: [online editing](#online-editing), [malware detection](#malware-detection),
[full-text search](#search), [storage quotas](#storage-quotas),
[the external API](#external-api), [usage metrics](#usage-metrics),
[Prometheus metrics](#prometheus-metrics) and [the file picker](#file-picker).

## Core

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE`{#DJANGO_SETTINGS_MODULE} | `drive.settings` | Python module holding the settings. Leave it unset |
| `DJANGO_CONFIGURATION`{#DJANGO_CONFIGURATION} | `Development` | `Production` on a server. It turns on the HTTPS redirect, secure cookies and HSTS, and adds the container's own address to the allowed hosts |
| `DJANGO_SECRET_KEY`{#DJANGO_SECRET_KEY} | none, *file* | Signs sessions and tokens. The backend does not start without it. Changing it signs everyone out |
| `DJANGO_ALLOWED_HOSTS`{#DJANGO_ALLOWED_HOSTS} | none | List of the host names the backend answers to |
| `DJANGO_CSRF_TRUSTED_ORIGINS`{#DJANGO_CSRF_TRUSTED_ORIGINS} | none | List of origins, `https://` included, allowed to send changes from another domain than the backend's |
| `DATA_DIR`{#DATA_DIR} | `/data` | Directory holding the static files the backend serves |
| `DJANGO_LANGUAGE_CODE`{#DJANGO_LANGUAGE_CODE} | `en-us` | Default language |
| `DJANGO_LANGUAGES`{#DJANGO_LANGUAGES} | English, French, German, Dutch | Languages a user can pick, as `code,name` pairs separated by `;` |

## Database

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL`{#DATABASE_URL} | none | A full address, `postgres://user:password@host:5432/name`. When set, `DB_ENGINE`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` and `DB_PASSWORD` are ignored; the `DB_PSYCOPG_POOL_` variables still apply |
| `DB_HOST`{#DB_HOST} | `localhost` | PostgreSQL host |
| `DB_PORT`{#DB_PORT} | `5432` | PostgreSQL port |
| `DB_NAME`{#DB_NAME} | `drive` | Database name |
| `DB_USER`{#DB_USER} | `dinum` | Database user |
| `DB_PASSWORD`{#DB_PASSWORD} | `pass`, *file* | Database password |
| `DB_ENGINE`{#DB_ENGINE} | `django.db.backends.postgresql` | Django database engine. Drive needs PostgreSQL |
| `DB_PSYCOPG_POOL_ENABLED`{#DB_PSYCOPG_POOL_ENABLED} | `False` | Keeps a pool of open connections in each process |
| `DB_PSYCOPG_POOL_MIN_SIZE`{#DB_PSYCOPG_POOL_MIN_SIZE} | `4` | Connections the pool keeps open |
| `DB_PSYCOPG_POOL_MAX_SIZE`{#DB_PSYCOPG_POOL_MAX_SIZE} | the minimum | Connections the pool may open at most |
| `DB_PSYCOPG_POOL_TIMEOUT`{#DB_PSYCOPG_POOL_TIMEOUT} | `3` | Seconds a request waits for a free connection |

## Cache and background tasks

Redis holds the cache, the sessions and the queue of background tasks.

| Variable | Default | Description |
| --- | --- | --- |
| `REDIS_URL`{#REDIS_URL} | `redis://redis:6379/0` | Redis for the cache and the sessions |
| `DJANGO_CELERY_BROKER_URL`{#DJANGO_CELERY_BROKER_URL} | `redis://redis:6379/0` | Queue of the background tasks |
| `DJANGO_CELERY_BROKER_TRANSPORT_OPTIONS`{#DJANGO_CELERY_BROKER_TRANSPORT_OPTIONS} | `{}` | Options of the queue's connection |
| `DJANGO_CELERY_TASK_ROUTES`{#DJANGO_CELERY_TASK_ROUTES} | `{}` | Sends some tasks to their own queue, so a worker can serve only them |
| `CACHES_DEFAULT_TIMEOUT`{#CACHES_DEFAULT_TIMEOUT} | `30` | Seconds a cached value lives, unless its code says otherwise |
| `CACHES_DEFAULT_KEY_PREFIX`{#CACHES_DEFAULT_KEY_PREFIX} | `drive` | Prefix of the cache keys, for a Redis shared with another app |
| `CACHES_SESSION_TIMEOUT`{#CACHES_SESSION_TIMEOUT} | `30` | Default seconds an entry lives in the session cache. Sessions set their own lifetime |

## File storage

Files live in an S3-compatible bucket. Browsers upload straight to it, so the
bucket needs a CORS rule allowing Drive's domain, while downloads go through
Drive at [`MEDIA_BASE_URL`](#MEDIA_BASE_URL).

| Variable | Default | Description |
| --- | --- | --- |
| `AWS_S3_ENDPOINT_URL`{#AWS_S3_ENDPOINT_URL} | none | Address of the S3 service, as the backend reaches it |
| `AWS_S3_DOMAIN_REPLACE`{#AWS_S3_DOMAIN_REPLACE} | none | Address of the S3 service as browsers reach it, when it differs from the backend's: upload addresses are signed for it |
| `AWS_S3_ACCESS_KEY_ID`{#AWS_S3_ACCESS_KEY_ID} | none, *file* | S3 access key |
| `AWS_S3_SECRET_ACCESS_KEY`{#AWS_S3_SECRET_ACCESS_KEY} | none, *file* | S3 secret key |
| `AWS_S3_REGION_NAME`{#AWS_S3_REGION_NAME} | none | S3 region |
| `AWS_STORAGE_BUCKET_NAME`{#AWS_STORAGE_BUCKET_NAME} | `drive-media-storage` | Bucket holding the files |
| `AWS_S3_SIGNATURE_VERSION`{#AWS_S3_SIGNATURE_VERSION} | `s3v4` | S3 signature version. Uploads need `s3v4` |
| `AWS_S3_UPLOAD_ACL`{#AWS_S3_UPLOAD_ACL} | `private` | Access rule signed into each upload. Set `default` for a storage without ACLs, such as Google Cloud Storage |
| `AWS_S3_UPLOAD_POLICY_EXPIRATION`{#AWS_S3_UPLOAD_POLICY_EXPIRATION} | `60` | Seconds an upload address stays valid |
| `MEDIA_BASE_URL`{#MEDIA_BASE_URL} | none | Drive's address. Download and preview addresses are built on it, under `/media/` |
| `STORAGES_DEFAULT_BACKEND`{#STORAGES_DEFAULT_BACKEND} | `storages.backends.s3.S3Storage` | Django storage class of the files |
| `DJANGO_STORAGES_STATICFILES_BACKEND`{#DJANGO_STORAGES_STATICFILES_BACKEND} | `whitenoise.storage.CompressedManifestStaticFilesStorage` | Django storage class of the static files |
| `S3_TRANSFER_CONFIG_USE_THREADS`{#S3_TRANSFER_CONFIG_USE_THREADS} | `True` | Lets the backend copy a file in parallel parts |
| `S3_TRANSFER_CONFIG_MULTIPART_THRESHOLD`{#S3_TRANSFER_CONFIG_MULTIPART_THRESHOLD} | `8388608` | Bytes above which the backend copies a file in parts |
| `S3_TRANSFER_CONFIG_MULTIPART_CHUNKSIZE`{#S3_TRANSFER_CONFIG_MULTIPART_CHUNKSIZE} | `8388608` | Bytes of each part |
| `S3_TRANSFER_CONFIG_MAX_CONCURRENCY`{#S3_TRANSFER_CONFIG_MAX_CONCURRENCY} | `10` | Parts copied at once |

The four `S3_TRANSFER_CONFIG_` variables matter only behind an encrypting proxy
that cannot handle parts, as [Encrypted storage](../self-hosting/configuration/encryption.md)
explains.

## Sign-in

Drive signs users in through an [OpenID Connect](https://openid.net/developers/how-connect-works/)
provider. [Sign-in](../self-hosting/configuration/authentication.md) walks
through the setup.

| Variable | Default | Description |
| --- | --- | --- |
| `OIDC_OP_AUTHORIZATION_ENDPOINT`{#OIDC_OP_AUTHORIZATION_ENDPOINT} | none | The provider's authorization address, which browsers open |
| `OIDC_OP_TOKEN_ENDPOINT`{#OIDC_OP_TOKEN_ENDPOINT} | none | The provider's token address |
| `OIDC_OP_USER_ENDPOINT`{#OIDC_OP_USER_ENDPOINT} | none | The provider's user information address |
| `OIDC_OP_JWKS_ENDPOINT`{#OIDC_OP_JWKS_ENDPOINT} | none | The provider's signing keys address |
| `OIDC_OP_LOGOUT_ENDPOINT`{#OIDC_OP_LOGOUT_ENDPOINT} | none | The provider's logout address |
| `OIDC_RP_CLIENT_ID`{#OIDC_RP_CLIENT_ID} | `drive` | Drive's client ID at the provider |
| `OIDC_RP_CLIENT_SECRET`{#OIDC_RP_CLIENT_SECRET} | none, *file* | Drive's client secret |
| `OIDC_RP_SIGN_ALGO`{#OIDC_RP_SIGN_ALGO} | `RS256` | Algorithm the provider signs its tokens with |
| `OIDC_RP_SCOPES`{#OIDC_RP_SCOPES} | `openid email` | Scopes Drive asks for, separated by spaces |
| `LOGIN_REDIRECT_URL`{#LOGIN_REDIRECT_URL} | none | Where a user lands after signing in |
| `LOGIN_REDIRECT_URL_FAILURE`{#LOGIN_REDIRECT_URL_FAILURE} | none | Where a user lands when signing in fails |
| `LOGOUT_REDIRECT_URL`{#LOGOUT_REDIRECT_URL} | none | Where a user lands after signing out |
| `OIDC_REDIRECT_ALLOWED_HOSTS`{#OIDC_REDIRECT_ALLOWED_HOSTS} | none | List of hosts Drive may send a user back to after signing in |
| `OIDC_REDIRECT_REQUIRE_HTTPS`{#OIDC_REDIRECT_REQUIRE_HTTPS} | `False` | Refuses to send a user back to a plain `http://` address |
| `OIDC_REDIRECT_FIELD_NAME`{#OIDC_REDIRECT_FIELD_NAME} | `returnTo` | Parameter carrying the page to go back to |
| `OIDC_AUTH_REQUEST_EXTRA_PARAMS`{#OIDC_AUTH_REQUEST_EXTRA_PARAMS} | `{}` | Extra parameters sent to the provider, such as `{"acr_values": "eidas1"}` |
| `OIDC_USE_NONCE`{#OIDC_USE_NONCE} | `True` | Sends and checks a nonce |
| `OIDC_USE_PKCE`{#OIDC_USE_PKCE} | `False` | Uses PKCE, for a provider that asks for it |
| `OIDC_PKCE_CODE_CHALLENGE_METHOD`{#OIDC_PKCE_CODE_CHALLENGE_METHOD} | `S256` | PKCE method |
| `OIDC_PKCE_CODE_VERIFIER_SIZE`{#OIDC_PKCE_CODE_VERIFIER_SIZE} | `64` | Length of the PKCE verifier |
| `DJANGO_OIDC_CREATE_USER`{#DJANGO_OIDC_CREATE_USER} | `True` | Creates the account of a user signing in for the first time |
| `OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION`{#OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION} | `True` | Finds an existing account by email when the provider's identifier is unknown |
| `OIDC_ALLOW_DUPLICATE_EMAILS`{#OIDC_ALLOW_DUPLICATE_EMAILS} | `False` | Allows two accounts with one email. The backend refuses to start with both this and the previous one on |
| `OIDC_USER_INFO`{#OIDC_USER_INFO}, or its old name `USER_OIDC_ESSENTIAL_CLAIMS`{#USER_OIDC_ESSENTIAL_CLAIMS} | none | Read by no code yet: Drive requires only the `sub` claim |
| `OIDC_USERINFO_FULLNAME_FIELDS`{#OIDC_USERINFO_FULLNAME_FIELDS} | `first_name,last_name` | Claims joined into the name Drive shows |
| `OIDC_USERINFO_SHORTNAME_FIELD`{#OIDC_USERINFO_SHORTNAME_FIELD} | `first_name` | Claim used as the short name |
| `OIDC_STORE_CLAIMS`{#OIDC_STORE_CLAIMS} | none | List of claims copied onto the user's account, for [usage metrics](#usage-metrics) |
| `OIDC_STORE_ID_TOKEN`{#OIDC_STORE_ID_TOKEN} | `True` | Keeps the ID token in the session, which signing out at the provider needs |
| `OIDC_STORE_ACCESS_TOKEN`{#OIDC_STORE_ACCESS_TOKEN} | `False` | Keeps the access token in the session, which [full-text search](#search) needs |
| `OIDC_STORE_REFRESH_TOKEN`{#OIDC_STORE_REFRESH_TOKEN} | `False` | Keeps the refresh token in the session, encrypted |
| `OIDC_STORE_REFRESH_TOKEN_KEY`{#OIDC_STORE_REFRESH_TOKEN_KEY} | none | Key encrypting that refresh token: 32 bytes, URL-safe base64 |
| `ALLOW_LOGOUT_GET_METHOD`{#ALLOW_LOGOUT_GET_METHOD} | `True` | Lets a plain link sign the user out |
| `FRONTEND_SILENT_LOGIN_ENABLED`{#FRONTEND_SILENT_LOGIN_ENABLED} | `False` | Signs a user in without a click when their provider session is still open |

## Email

Drive sends an email when a file is shared with someone. With no
[`DJANGO_EMAIL_HOST`](#DJANGO_EMAIL_HOST), it sends none.

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_EMAIL_HOST`{#DJANGO_EMAIL_HOST} | none | SMTP server |
| `DJANGO_EMAIL_PORT`{#DJANGO_EMAIL_PORT} | none | SMTP port |
| `DJANGO_EMAIL_HOST_USER`{#DJANGO_EMAIL_HOST_USER} | none | SMTP user |
| `DJANGO_EMAIL_HOST_PASSWORD`{#DJANGO_EMAIL_HOST_PASSWORD} | none, *file* | SMTP password |
| `DJANGO_EMAIL_USE_TLS`{#DJANGO_EMAIL_USE_TLS} | `False` | Uses STARTTLS |
| `DJANGO_EMAIL_USE_SSL`{#DJANGO_EMAIL_USE_SSL} | `False` | Uses TLS from the first byte |
| `DJANGO_EMAIL_FROM`{#DJANGO_EMAIL_FROM} | `from@example.com` | Sender address |
| `DJANGO_EMAIL_URL_APP`{#DJANGO_EMAIL_URL_APP} | none | Drive's address, which the links in emails start with |
| `DJANGO_EMAIL_BACKEND`{#DJANGO_EMAIL_BACKEND} | `django.core.mail.backends.smtp.EmailBackend` | Django email class |
| `DJANGO_EMAIL_APP_NAME`{#DJANGO_EMAIL_APP_NAME} | `Drive` | Product name in the emails |
| `DJANGO_EMAIL_BRAND_NAME`{#DJANGO_EMAIL_BRAND_NAME} | none | Brand name in the emails |
| `DJANGO_EMAIL_LOGO_IMG`{#DJANGO_EMAIL_LOGO_IMG} | none | Address of the logo at the top of the emails |
| `DJANGO_EMAIL_FONT_FAMILY`{#DJANGO_EMAIL_FONT_FAMILY} | `Marianne` | Font of the emails |
| `DJANGO_EMAIL_FONT_REGULAR_URL`{#DJANGO_EMAIL_FONT_REGULAR_URL} | none | Address of that font's regular `.woff2` |
| `DJANGO_EMAIL_FONT_BOLD_URL`{#DJANGO_EMAIL_FONT_BOLD_URL} | none | Address of that font's bold `.woff2` |
| `DJANGO_EMAIL_GOVERNMENT_LOGO_IMG`{#DJANGO_EMAIL_GOVERNMENT_LOGO_IMG} | none | Logo at the bottom of the emails, hidden when unset |
| `DJANGO_EMAIL_NEWSLETTER_URL`{#DJANGO_EMAIL_NEWSLETTER_URL} | none | Newsletter link at the bottom, hidden when unset |
| `DJANGO_EMAIL_SUPPORT_URL`{#DJANGO_EMAIL_SUPPORT_URL} | none | Support link at the bottom |
| `DJANGO_EMAIL_TERMS_OF_SERVICE_URL`{#DJANGO_EMAIL_TERMS_OF_SERVICE_URL} | none | Terms of service link at the bottom |
| `DJANGO_EMAIL_SUITE_LOGO_IMG`{#DJANGO_EMAIL_SUITE_LOGO_IMG} | none | Suite logo at the bottom |
| `DJANGO_EMAIL_SUITE_URL`{#DJANGO_EMAIL_SUITE_URL} | none | Link of that suite logo |
| `DJANGO_EMAIL_PRODUCT_ICONS`{#DJANGO_EMAIL_PRODUCT_ICONS} | `{}` | Icons of the other apps, `{"Docs": {"img": "<address>", "href": "<address>"}}` |

## Uploads

| Variable | Default | Description |
| --- | --- | --- |
| `DATA_UPLOAD_MAX_MEMORY_SIZE`{#DATA_UPLOAD_MAX_MEMORY_SIZE} | `2147483648`, 2 GB | Largest file a user can upload, in bytes |
| `RESTRICT_UPLOAD_FILE_TYPE`{#RESTRICT_UPLOAD_FILE_TYPE} | `allowlist` | `allowlist` accepts only the types of the two `_ALLOWED` lists, `denylist` refuses the types of the two `_DENIED` lists, `off` accepts everything. Any other value stops the backend |
| `FILE_EXTENSIONS_ALLOWED`{#FILE_EXTENSIONS_ALLOWED} | a built-in list | Extensions accepted with `allowlist` |
| `FILE_MIMETYPE_ALLOWED`{#FILE_MIMETYPE_ALLOWED} | a built-in list | File types accepted with `allowlist`. The type is read from the file's first bytes, or from its extension when those bytes give only a generic type such as `application/zip` |
| `FILE_EXTENSIONS_DENIED`{#FILE_EXTENSIONS_DENIED} | a built-in list of executables and scripts | Extensions refused with `denylist` |
| `FILE_MIMETYPE_DENIED`{#FILE_MIMETYPE_DENIED} | a built-in list | File types refused with `denylist` |
| `ITEM_PREVIEWABLE_MIME_TYPES`{#ITEM_PREVIEWABLE_MIME_TYPES} | `image/,video/,audio/,application/pdf` | File types Drive shows in its viewer |
| `MAX_PAGE_SIZE`{#MAX_PAGE_SIZE} | `200` | Most items one API call can list |

## Trash and clean-up

| Variable | Default | Description |
| --- | --- | --- |
| `TRASHBIN_CUTOFF_DAYS`{#TRASHBIN_CUTOFF_DAYS} | `30` | Days a deleted item can be restored from the trash. Leave it at the default for now: a value set here is read as text, and the trash and the purge then fail |
| `PURGE_GRACE_DAYS`{#PURGE_GRACE_DAYS} | `7` | Days after that before the purge erases it from the database and the bucket. Leave it at the default for now: a value set here is read as text, and the trash and the purge then fail |
| `PURGE_DELETED_ITEMS_SCHEDULE`{#PURGE_DELETED_ITEMS_SCHEDULE} | none | When Celery beat runs the purge: a crontab line, then the command's options. Unset, it never runs: run `purge_deleted_items` another way, as the Helm chart's cron job does |
| `CLEAN_PENDING_ITEMS_SCHEDULE`{#CLEAN_PENDING_ITEMS_SCHEDULE} | none | When Celery beat deletes uploads never finished, such as `30 0 * * * --hours=48` |

## Sharing

| Variable | Default | Description |
| --- | --- | --- |
| `INVITATION_VALIDITY_DURATION`{#INVITATION_VALIDITY_DURATION} | `604800`, 7 days | Seconds an invitation to an email with no account stays valid |
| `ALLOW_SHARE_IMPORT_FILE`{#ALLOW_SHARE_IMPORT_FILE} | `False` | Lets users share with every address of an imported contacts file |
| `API_USERS_LIST_LIMIT`{#API_USERS_LIST_LIMIT} | `5` | People the share dialog suggests at most |
| `FEATURES_RESTRICTED_FOLDERS_USERS`{#FEATURES_RESTRICTED_FOLDERS_USERS} | none | List of the emails of the users who may restrict a folder to the people named on it |
| `PERMISSIONS_BACKEND`{#PERMISSIONS_BACKEND} | `core.permissions.backends.role.RolePermissionsBackend` | Class deciding what each role allows |
| `PERMISSIONS_BACKEND_PARAMETERS`{#PERMISSIONS_BACKEND_PARAMETERS} | `{}` | Parameters of that class |
| `USER_RECONCILIATION_FORM_URL`{#USER_RECONCILIATION_FORM_URL} | none | Form the email links when [merging two accounts](../self-hosting/configuration/account-merging.md) fails |

## Online editing

[Online editing](../self-hosting/configuration/online-editing.md) explains the
setup. `<CLIENT>` is an editor's name from [`WOPI_CLIENTS`](#WOPI_CLIENTS), in
capitals: `WOPI_COLLABORA_DISCOVERY_URL`.

| Variable | Default | Description |
| --- | --- | --- |
| `WOPI_CLIENTS`{#WOPI_CLIENTS} | none | List of the editors to use, such as `collabora` or `onlyoffice` |
| `WOPI_<CLIENT>_DISCOVERY_URL`{#WOPI_CLIENT_DISCOVERY_URL} | none | The editor's discovery address. Required for each editor listed |
| `WOPI_<CLIENT>_OPTIONS`{#WOPI_CLIENT_OPTIONS} | `{}` | The editor's options: `SupportsRename`, `ForceConvertExtensions`, `ForceConvertMimetypes`, `ConvertServiceUrl` |
| `WOPI_SRC_BASE_URL`{#WOPI_SRC_BASE_URL} | none | The backend's address as the editor reaches it |
| `WOPI_EXCLUDED_MIMETYPES`{#WOPI_EXCLUDED_MIMETYPES} | images and PDF | File types never opened in an editor |
| `WOPI_EXCLUDED_EXTENSIONS`{#WOPI_EXCLUDED_EXTENSIONS} | `svg,png,jpg,jpeg,gif,bmp,tiff,webp,pdf` | Extensions never opened in an editor |
| `WOPI_ACCESS_TOKEN_TIMEOUT`{#WOPI_ACCESS_TOKEN_TIMEOUT} | `36000` | Seconds an editing session's token stays valid |
| `WOPI_LOCK_TIMEOUT`{#WOPI_LOCK_TIMEOUT} | `1800` | Seconds an editor's lock on a file lasts without being renewed |
| `WOPI_DISABLE_CHAT`{#WOPI_DISABLE_CHAT} | `0` | `1` hides the editor's chat |
| `WOPI_CONFIGURATION_CACHE_EXPIRATION`{#WOPI_CONFIGURATION_CACHE_EXPIRATION} | `86400` | Seconds the editors' discovery stays cached |
| `WOPI_CONFIGURATION_CRONTAB_MINUTE`{#WOPI_CONFIGURATION_CRONTAB_MINUTE} | `0` | Minute Celery beat reads the discovery again |
| `WOPI_CONFIGURATION_CRONTAB_HOUR`{#WOPI_CONFIGURATION_CRONTAB_HOUR} | `3` | Hour of that refresh |
| `WOPI_CONFIGURATION_CRONTAB_DAY_OF_MONTH`{#WOPI_CONFIGURATION_CRONTAB_DAY_OF_MONTH} | `*` | Days of the month of that refresh |
| `WOPI_CONFIGURATION_CRONTAB_MONTH_OF_YEAR`{#WOPI_CONFIGURATION_CRONTAB_MONTH_OF_YEAR} | `*` | Months of that refresh |
| `WOPI_ONLYOFFICE_CONVERT_JWT_SECRET`{#WOPI_ONLYOFFICE_CONVERT_JWT_SECRET} | none, *file* | OnlyOffice's JWT secret. Converting `.doc`, `.xls` and `.ppt` files needs it |
| `WOPI_CONVERSION_SOURCE_TOKEN_TIMEOUT`{#WOPI_CONVERSION_SOURCE_TOKEN_TIMEOUT} | `120` | Seconds OnlyOffice has to fetch the file it converts |
| `WOPI_ONLYOFFICE_CONVERT_HTTP_CONNECT_TIMEOUT`{#WOPI_ONLYOFFICE_CONVERT_HTTP_CONNECT_TIMEOUT} | `5` | Seconds to reach the conversion service |
| `WOPI_ONLYOFFICE_CONVERT_HTTP_READ_TIMEOUT`{#WOPI_ONLYOFFICE_CONVERT_HTTP_READ_TIMEOUT} | `60` | Seconds to wait for the conversion |
| `WOPI_ONLYOFFICE_CONVERT_DOWNLOAD_CONNECT_TIMEOUT`{#WOPI_ONLYOFFICE_CONVERT_DOWNLOAD_CONNECT_TIMEOUT} | `5` | Seconds to reach the converted file |
| `WOPI_ONLYOFFICE_CONVERT_DOWNLOAD_READ_TIMEOUT`{#WOPI_ONLYOFFICE_CONVERT_DOWNLOAD_READ_TIMEOUT} | `30` | Seconds to download the converted file |

## Malware detection

[Malware detection](../self-hosting/configuration/malware-detection.md)
explains the setup.

| Variable | Default | Description |
| --- | --- | --- |
| `MALWARE_DETECTION_BACKEND`{#MALWARE_DETECTION_BACKEND} | `lasuite.malware_detection.backends.dummy.DummyBackend` | Class sending files to the scanner. The default scans nothing and marks every file safe |
| `MALWARE_DETECTION_DUMMY_SLEEP`{#MALWARE_DETECTION_DUMMY_SLEEP} | `3` | Seconds the development scanner waits before marking a file safe |
| `MALWARE_DETECTION_PARAMETERS`{#MALWARE_DETECTION_PARAMETERS} | `{"callback_path": "core.malware_detection.malware_detection_callback"}` | Parameters of that class. Keep `callback_path` when adding yours |

## Search

[Full-text search](../self-hosting/configuration/search.md) explains the
setup. Without [`SEARCH_INDEXER_CLASS`](#SEARCH_INDEXER_CLASS), search matches
names only.

| Variable | Default | Description |
| --- | --- | --- |
| `SEARCH_INDEXER_CLASS`{#SEARCH_INDEXER_CLASS} | none | `core.services.search_indexers.SearchIndexer` sends files to Find |
| `SEARCH_INDEXER_URL`{#SEARCH_INDEXER_URL} | none | Find's indexing address |
| `SEARCH_INDEXER_QUERY_URL`{#SEARCH_INDEXER_QUERY_URL} | none | Find's search address |
| `SEARCH_INDEXER_SECRET`{#SEARCH_INDEXER_SECRET} | none | The token of Drive's service in Find |
| `SEARCH_INDEXER_COUNTDOWN`{#SEARCH_INDEXER_COUNTDOWN} | `1` | Seconds Drive waits after a change before indexing, so a burst of changes is sent once |
| `SEARCH_INDEXER_QUERY_LIMIT`{#SEARCH_INDEXER_QUERY_LIMIT} | `50` | Results asked from Find at most |
| `SEARCH_INDEXER_CONTENT_MAX_SIZE`{#SEARCH_INDEXER_CONTENT_MAX_SIZE} | `2097152`, 2 MB | Largest file whose text is indexed, in bytes |
| `SEARCH_INDEXER_ALLOWED_MIMETYPES`{#SEARCH_INDEXER_ALLOWED_MIMETYPES} | `text/` | List of the file types whose text is indexed |
| `SEARCH_INDEXER_BATCH_SIZE`{#SEARCH_INDEXER_BATCH_SIZE} | `100000` | Items sent per batch by the `index` command |
| `FEATURES_INDEXED_SEARCH`{#FEATURES_INDEXED_SEARCH} | `True` | Searches through Find when an indexer is set |

## Storage quotas

[Storage quotas](../self-hosting/configuration/quotas.md) explains the setup.

| Variable | Default | Description |
| --- | --- | --- |
| `ENTITLEMENTS_BACKEND`{#ENTITLEMENTS_BACKEND} | `core.entitlements.backends.static.StaticEntitlementsBackend` | Class deciding who may sign in and upload. The default allows everyone |
| `ENTITLEMENTS_BACKEND_PARAMETERS`{#ENTITLEMENTS_BACKEND_PARAMETERS} | `{}` | Parameters of that class |
| `STORAGE_COMPUTE_BACKEND`{#STORAGE_COMPUTE_BACKEND} | `core.storage.creator_storage_compute_backend.CreatorStorageComputeBackend` | Class computing a user's storage: by default, the size of the files they created |
| `FRONTEND_ENTITLEMENTS_DISCLAIMERS`{#FRONTEND_ENTITLEMENTS_DISCLAIMERS} | `{}` | Messages shown to users who cannot upload |

## Look and feel

[Look and feel](../self-hosting/configuration/theming.md) explains these.

| Variable | Default | Description |
| --- | --- | --- |
| `FRONTEND_THEME`{#FRONTEND_THEME} | none | Name of a built-in theme, such as `dsfr-light` |
| `FRONTEND_CSS_URL`{#FRONTEND_CSS_URL} | none | Address of a stylesheet loaded after Drive's own |
| `FRONTEND_JS_URL`{#FRONTEND_JS_URL} | none | Address of a script loaded in every page |
| `THEME_CUSTOMIZATION_FILE_PATH`{#THEME_CUSTOMIZATION_FILE_PATH} | `drive/configuration/theme/default.json`, in the image | JSON file describing the footer |
| `THEME_CUSTOMIZATION_CACHE_TIMEOUT`{#THEME_CUSTOMIZATION_CACHE_TIMEOUT} | `86400` | Seconds that file stays cached. Leave it at the default for now: a value set here is read as text and gives the cache a wrong lifetime |
| `FRONTEND_HIDE_GAUFRE`{#FRONTEND_HIDE_GAUFRE} | `False` | Hides the menu of La Suite's other apps |
| `FRONTEND_EXTERNAL_HOME_URL`{#FRONTEND_EXTERNAL_HOME_URL} | none | Sends visitors of the home page there instead |
| `FRONTEND_MORE_LINK`{#FRONTEND_MORE_LINK} | none | Address of the home page's **Learn more** button |
| `FRONTEND_HELP_MENU_CONFIG`{#FRONTEND_HELP_MENU_CONFIG} | `{}` | Help menu of the sidebar: `documentationUrl`, `supportEmail` and the `legal` links. No menu when empty |
| `FRONTEND_RELEASE_NOTE_ENABLED`{#FRONTEND_RELEASE_NOTE_ENABLED} | `True` | Shows the **What's new** window after an upgrade |
| `FRONTEND_STORAGE_GAUGE_INFORMATION_LINK`{#FRONTEND_STORAGE_GAUGE_INFORMATION_LINK} | none | Link under the storage gauge |

## Feedback and analytics

| Variable | Default | Description |
| --- | --- | --- |
| `FRONTEND_FEEDBACK_BUTTON_SHOW`{#FRONTEND_FEEDBACK_BUTTON_SHOW} | `False` | Shows a **Give feedback** button |
| `FRONTEND_FEEDBACK_BUTTON_IDLE`{#FRONTEND_FEEDBACK_BUTTON_IDLE} | `False` | The button does nothing itself, for a survey tool to hook into |
| `FRONTEND_FEEDBACK_ITEMS`{#FRONTEND_FEEDBACK_ITEMS} | `{}` | Entries of the button's menu, each with its `url` |
| `FRONTEND_FEEDBACK_MESSAGES_WIDGET_ENABLED`{#FRONTEND_FEEDBACK_MESSAGES_WIDGET_ENABLED} | `False` | Shows a messages widget |
| `FRONTEND_FEEDBACK_MESSAGES_WIDGET_API_URL`{#FRONTEND_FEEDBACK_MESSAGES_WIDGET_API_URL} | none | Address of the widget's service |
| `FRONTEND_FEEDBACK_MESSAGES_WIDGET_CHANNEL`{#FRONTEND_FEEDBACK_MESSAGES_WIDGET_CHANNEL} | none | Channel of the widget |
| `FRONTEND_FEEDBACK_MESSAGES_WIDGET_PATH`{#FRONTEND_FEEDBACK_MESSAGES_WIDGET_PATH} | none | Path of the widget |
| `POSTHOG_KEY`{#POSTHOG_KEY} | none, *file* | PostHog project key. Usage analytics stay off without it |
| `POSTHOG_HOST`{#POSTHOG_HOST} | `https://eu.i.posthog.com` | PostHog address |
| `CRISP_WEBSITE_ID`{#CRISP_WEBSITE_ID} | none | Crisp chat website ID, sent to the browser. The frontend does not use it |

[`POSTHOG_KEY`](#POSTHOG_KEY) and [`SENTRY_DSN`](#SENTRY_DSN) are sent to every
browser, signed in or not, since the pages use them.

## External API

[External API](../integrating/external-api.md) explains these.

| Variable | Default | Description |
| --- | --- | --- |
| `OIDC_RESOURCE_SERVER_ENABLED`{#OIDC_RESOURCE_SERVER_ENABLED} | `False` | Serves `/external_api/v1.0/` to other applications holding a user's token |
| `EXTERNAL_API`{#EXTERNAL_API} | items: `create`, `list`, `retrieve`, `children`, `upload_ended`; users: `get_me` | Routes and actions the external API allows |
| `EXTERNAL_API_AUD_ITEM_ATTRIBUTES`{#EXTERNAL_API_AUD_ITEM_ATTRIBUTES} | `{}` | Attributes given to items created by each calling application |
| `OIDC_OP_URL`{#OIDC_OP_URL} | none | The provider's issuer address |
| `OIDC_OP_INTROSPECTION_ENDPOINT`{#OIDC_OP_INTROSPECTION_ENDPOINT} | none | The provider's token introspection address |
| `OIDC_RS_CLIENT_ID`{#OIDC_RS_CLIENT_ID} | none | Drive's client ID as a resource server |
| `OIDC_RS_CLIENT_SECRET`{#OIDC_RS_CLIENT_SECRET} | none | Drive's client secret as a resource server |
| `OIDC_RS_AUDIENCE_CLAIM`{#OIDC_RS_AUDIENCE_CLAIM} | `client_id` | Claim naming the calling application |
| `OIDC_RS_ALLOWED_AUDIENCES`{#OIDC_RS_ALLOWED_AUDIENCES} | none | List of the applications allowed to call |
| `OIDC_RS_SCOPES`{#OIDC_RS_SCOPES} | `openid` | List of scopes a token must hold one of |
| `OIDC_RS_BACKEND_CLASS`{#OIDC_RS_BACKEND_CLASS} | `lasuite.oidc_resource_server.backend.ResourceServerBackend` | Class checking the tokens |
| `OIDC_RS_SIGNING_ALGO`{#OIDC_RS_SIGNING_ALGO} | `ES256` | Signing algorithm of encrypted introspection |
| `OIDC_RS_ENCRYPTION_ALGO`{#OIDC_RS_ENCRYPTION_ALGO} | `RSA-OAEP` | Encryption algorithm of encrypted introspection |
| `OIDC_RS_ENCRYPTION_ENCODING`{#OIDC_RS_ENCRYPTION_ENCODING} | `A256GCM` | Encryption encoding of encrypted introspection |
| `OIDC_RS_ENCRYPTION_KEY_TYPE`{#OIDC_RS_ENCRYPTION_KEY_TYPE} | `RSA` | Key type of encrypted introspection |
| `OIDC_RS_PRIVATE_KEY_STR`{#OIDC_RS_PRIVATE_KEY_STR} | none | Private key for encrypted introspection. When set, Drive also publishes its public keys |
| `OIDC_VERIFY_SSL`{#OIDC_VERIFY_SSL} | `True` | Checks the provider's certificate |
| `OIDC_TIMEOUT`{#OIDC_TIMEOUT} | `3` | Seconds to wait for the provider |
| `OIDC_PROXY`{#OIDC_PROXY} | none | Proxy to reach the provider through |

## Usage metrics

| Variable | Default | Description |
| --- | --- | --- |
| `METRICS_ENABLED`{#METRICS_ENABLED} | `False` | Serves the [usage metrics route](../integrating/usage-metrics.md) |
| `METRICS_USER_CLAIMS_EXPOSED`{#METRICS_USER_CLAIMS_EXPOSED} | none | List of stored claims the route adds to each user |

## Prometheus metrics

[Monitoring](../self-hosting/configuration/monitoring.md) explains these.

| Variable | Default | Description |
| --- | --- | --- |
| `PROMETHEUS_METRICS_ENABLED`{#PROMETHEUS_METRICS_ENABLED} | `False` | Serves the metrics on `/metrics` |
| `PROMETHEUS_API_KEY`{#PROMETHEUS_API_KEY} | none, *file* | Bearer token `/metrics` requires. The backend refuses to start with the metrics on and no token |
| `PROMETHEUS_METRICS_SSL_REDIRECT_EXEMPT`{#PROMETHEUS_METRICS_SSL_REDIRECT_EXEMPT} | `False` | Serves `/metrics` over plain HTTP too |
| `PROMETHEUS_DB_METRICS_ENABLED`{#PROMETHEUS_DB_METRICS_ENABLED} | `True` | Counts and times the SQL queries |
| `PROMETHEUS_CELERY_QUEUE_METRICS_ENABLED`{#PROMETHEUS_CELERY_QUEUE_METRICS_ENABLED} | `True` | Reports the length of the task queue |
| `PROMETHEUS_BUSINESS_METRICS_ENABLED`{#PROMETHEUS_BUSINESS_METRICS_ENABLED} | `True` | Reports the counts of items, users and storage |
| `PROMETHEUS_BUSINESS_METRICS_CACHE_TTL`{#PROMETHEUS_BUSINESS_METRICS_CACHE_TTL} | `300` | Seconds those counts stay cached |
| `PROMETHEUS_MULTIPROC_DIR`{#PROMETHEUS_MULTIPROC_DIR} | a directory under the system's temporary one | Directory the backend's processes share their metrics through |

## File picker

The file picker lets another La Suite app open Drive in a window to choose
files.

| Variable | Default | Description |
| --- | --- | --- |
| `SDK_ENABLED`{#SDK_ENABLED} | `False` | Serves the picker |
| `SDK_CORS_ALLOWED_ORIGINS`{#SDK_CORS_ALLOWED_ORIGINS} | none | List of the apps' origins allowed to use it |
| `SDK_RELAY_CACHE_TIMEOUT`{#SDK_RELAY_CACHE_TIMEOUT} | `600` | Seconds the picker's messages to the app stay available |

## Rate limits

| Variable | Default | Description |
| --- | --- | --- |
| `API_USERS_LIST_THROTTLE_RATE_SUSTAINED`{#API_USERS_LIST_THROTTLE_RATE_SUSTAINED} | `180/hour` | People searches per user, over an hour |
| `API_USERS_LIST_THROTTLE_RATE_BURST`{#API_USERS_LIST_THROTTLE_RATE_BURST} | `30/minute` | People searches per user, over a minute |
| `API_ITEMS_CREATE_THROTTLE_RATE_SUSTAINED`{#API_ITEMS_CREATE_THROTTLE_RATE_SUSTAINED} | `5000/hour` | Files and folders created per user, over an hour |
| `API_ITEMS_CREATE_THROTTLE_RATE_BURST`{#API_ITEMS_CREATE_THROTTLE_RATE_BURST} | `300/minute` | Files and folders created per user, over a minute |
| `API_ITEMS_UNLOCK_THROTTLE_RATE`{#API_ITEMS_UNLOCK_THROTTLE_RATE} | `10/minute` | Attempts at a protected link's password |
| `API_SDK_EVENT_RELAY_THROTTLE_RATE`{#API_SDK_EVENT_RELAY_THROTTLE_RATE} | `200/minute` | Calls to the file picker's relay |

## Logs and errors

| Variable | Default | Description |
| --- | --- | --- |
| `LOGGING_LEVEL_LOGGERS_ROOT`{#LOGGING_LEVEL_LOGGERS_ROOT} | `INFO` | Log level of the libraries |
| `LOGGING_LEVEL_LOGGERS_APP`{#LOGGING_LEVEL_LOGGERS_APP} | `INFO` | Log level of Drive's own code |
| `SENTRY_DSN`{#SENTRY_DSN} | none | Sends errors to Sentry |
| `SENTRY_TRACES_SAMPLE_RATE`{#SENTRY_TRACES_SAMPLE_RATE} | `0.0` | Share of requests whose timing is sent to Sentry, from `0.0` to `1.0` |
| `DJANGO_SPECTACULAR_SETTINGS_ENABLE_DJANGO_DEPLOY_CHECK`{#DJANGO_SPECTACULAR_SETTINGS_ENABLE_DJANGO_DEPLOY_CHECK} | `False` | Runs the API schema's checks with Django's deployment checks |

## Cross-origin requests

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_CORS_ALLOW_ALL_ORIGINS`{#DJANGO_CORS_ALLOW_ALL_ORIGINS} | `False` | Lets any website call the API from a browser |
| `DJANGO_CORS_ALLOWED_ORIGINS`{#DJANGO_CORS_ALLOWED_ORIGINS} | none | List of the websites allowed to |
| `DJANGO_CORS_ALLOWED_ORIGIN_REGEXES`{#DJANGO_CORS_ALLOWED_ORIGIN_REGEXES} | none | List of patterns of the websites allowed to |

## Frontend image

The frontend is built into static files, so its one setting is fixed when the
image is built, not when it runs:

| Build argument | Default | Description |
| --- | --- | --- |
| `API_ORIGIN`{#API_ORIGIN} | the page's own address | The backend's address, when it is not served on the frontend's domain |
