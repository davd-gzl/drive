# Encrypted storage

[DS Proxy](https://github.com/demarche-numerique/ds_proxy) sits between Drive
and the bucket: it encrypts each file on its way in and decrypts it on its way
out, so the bucket only ever holds encrypted files. It speaks the S3 API, so
Drive only needs its address in place of the bucket's.

## Point Drive at the proxy

Every address Drive uses for the bucket goes through the proxy instead:

| Setting | Points to |
| --- | --- |
| [`AWS_S3_ENDPOINT_URL`](../../reference/env-variables.md#AWS_S3_ENDPOINT_URL) | The proxy, as the backend reaches it, with its `/upstream` path |
| [`AWS_S3_DOMAIN_REPLACE`](../../reference/env-variables.md#AWS_S3_DOMAIN_REPLACE) | The proxy, as browsers reach it, since they upload to it |
| The media proxy | The proxy, for downloads: the `upstream-vhost` annotation and `serviceMedia.host` in the Helm chart, the `proxy_pass` of the `/media/` locations with nginx |

## Turn off multipart transfers

The S3 client Drive uses splits large copies and reads into parts and adds
checksums, which DS Proxy does not support. Turn both off on the backend:

```bash title="Backend environment"
AWS_REQUEST_CHECKSUM_CALCULATION=when_required
AWS_RESPONSE_CHECKSUM_VALIDATION=when_required
S3_TRANSFER_CONFIG_USE_THREADS=False
S3_TRANSFER_CONFIG_MULTIPART_THRESHOLD=10737418240
S3_TRANSFER_CONFIG_MULTIPART_CHUNKSIZE=10737418240
S3_TRANSFER_CONFIG_MAX_CONCURRENCY=1
```

The first two are read by the S3 library itself, the others by Drive. A
threshold of 10 GiB keeps every file in one part.

## Try it locally

The development stack ships a `ds-proxy` service, off by default:

1. In `env.d/development/common.local`, set
   `AWS_S3_ENDPOINT_URL=http://ds-proxy:4444/upstream` and
   `AWS_S3_DOMAIN_REPLACE=http://localhost:4444/upstream`.
2. In
   [`docker/files/development/etc/nginx/conf.d/default.conf`](https://github.com/suitenumerique/drive/blob/main/docker/files/development/etc/nginx/conf.d/default.conf),
   in both `/media/` locations, comment out the RustFS `proxy_pass` and
   `proxy_set_header` lines and uncomment the DS Proxy ones.
3. Run `make run-backend`, then `docker compose up -d ds-proxy`.

On the Tilt stack, set `dsproxy.enabled` to `true` in
[`src/helm/helmfile.yaml.gotmpl`](https://github.com/suitenumerique/drive/blob/main/src/helm/helmfile.yaml.gotmpl),
then in `src/helm/env.d/dev/values.drive.yaml.gotmpl` swap the commented
`AWS_S3_ENDPOINT_URL`, `upstream-vhost` and `serviceMedia.host` lines for the
DS Proxy ones.
