# Usage metrics

Drive provides a route to export metrics to external tools. At the moment, only the `storage_used` metric is exposed.

For monitoring with Prometheus and Grafana, see
[Monitoring](../self-hosting/configuration/monitoring.md).

The route is:

`GET /external_api/v1.0/metrics/usage/`

You must provide an authorization header as follows:

```
Authorization: Api-Key <key>
```

`account_type=user|organization` picks the accounts. It defaults to `user`.

## Enabling

The route is off until
[`METRICS_ENABLED`](../reference/env-variables.md#METRICS_ENABLED) is `True`.

## How to get the API key

In the Django admin, open **API keys**, add one, give it a name and save. The
admin then shows the key in a warning at the top of the page.

!!! warning

    The key is shown this once only: copy it to a safe place.

## Response

The response will look like this:

```
{
    "count": 123,
    "next": null,
    "previous": null,
    "results": [
        {
            "account": {
                "type": "user",
                "id": "<sub>",
                "email": "john.doe@example.com",
            },
            "metrics": {
                "storage_used": 100,
            },
        },
        {
            "account": {
                "type": "user",
                "id": "<sub>",
                "email": "johnette.doe@example.com",
            },
            "metrics": {
                "storage_used": 0,
            },
        },
        ...
    ],
}
```

Each entry corresponds to a user. The response format is designed to match this spec: https://docs.numerique.gouv.fr/docs/14c29262-e9ce-486a-9ced-3c766bd8abf7/

The `storage_used` is, by default, the sum of the sizes of the files the user
created, in bytes. Files in the trash count until they are deleted for good,
and files marked `quota_excluded` do not count.

## Filtering

You can filter this by using `account_id_key` and `account_id_value` query parameter like so:

- `account_type` | `user` or `organization`
- `account_id_key` | The key to filter on (`sub` or `email` for `account_type=user`). Required if `account_type=organization`, it could be any oidc stored claim.
- `account_id_value` | The value to filter on. Required if `account_type=organization`.
- `account_email` | Same as `account_id_key=email&account_id_value=<email>`, kept for older callers.

Examples:

```
GET /external_api/v1.0/metrics/usage/?account_type=user
GET /external_api/v1.0/metrics/usage/?account_type=user&account_id_key=sub&account_id_value=<sub value>
GET /external_api/v1.0/metrics/usage/?account_type=user&account_email=<email>
GET /external_api/v1.0/metrics/usage/?account_type=organization # 400: account_id_key and account_id_value are required
GET /external_api/v1.0/metrics/usage/?account_type=organization&account_id_key=siret&account_id_value=<siret value>
```

## How to customize the storage used computation?

The way the `storage_used` metric is computed may not match the way you want it to work. To customize it, you will need to customize the `STORAGE_COMPUTE_BACKEND` setting and provide a custom implementation that extends `StorageComputeBackend`.

You can see the default implementation `CreatorStorageComputeBackend` as an example.

## Expose OIDC claims

For aggregation purposes, you might want to expose some OIDC claims from this route that your external tool will use.

For instance, with the deploy center, the implementation needs to get access to the `siret` claim.

Simply customize the setting `METRICS_USER_CLAIMS_EXPOSED=your_claim1,your_claim2` and the response will look like this:

```
{
    "count": 123,
    "next": null,
    "previous": null,
    "results": [
        {
            "account": {
                "type": "user",
                "id": "<sub>",
                "email": "john.doe@example.com",
            },
            "your_claim1": <value>,
            "your_claim2": <value>,
            "metrics": {
                "storage_used": 100,
            },
        },
        ...
    ],
}
```

!!! warning

    List the same claims in
    [`OIDC_STORE_CLAIMS`](../reference/env-variables.md#OIDC_STORE_CLAIMS),
    or Drive never stores them and the route returns none.

## Organization metrics

To sum the storage of every user sharing a claim's value, an organisation's
`siret` for instance, pass `account_type=organization` with `account_id_key`,
the name of a stored claim, and `account_id_value`, its value. Both are
required with `organization`.

Add `siret` to
[`OIDC_STORE_CLAIMS`](../reference/env-variables.md#OIDC_STORE_CLAIMS), so it
is stored on each user.

Example:

```
GET /external_api/v1.0/metrics/usage/?account_type=organization&account_id_key=siret&account_id_value=12345678900001
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "account": {
                "type": "organization",
            },
            "siret": "12345678900001",
            "metrics": {
                "storage_used": 10000000,
            },
        },
    ],
}
```
