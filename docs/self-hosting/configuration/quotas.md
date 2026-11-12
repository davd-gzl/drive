# Storage quotas

Drive decides who may sign in and who may upload through an *entitlements
backend*. The default one allows everyone everything. The local one gives each
user a storage limit, and a backend of your own can apply any rule.

## Limit each user's storage

```bash title="Backend environment"
ENTITLEMENTS_BACKEND=core.entitlements.backends.local.LocalEntitlementsBackend
ENTITLEMENTS_BACKEND_PARAMETERS={"default_storage_limit": 10737418240}
```

Each user may then store 10 GiB, the size of the files they created. Users see
a gauge of their storage in the sidebar, and an upload is refused once they are
over their limit. The check compares what the user already stores with the
limit, so one upload can still go past it; the next one is refused.

The parameters, all optional:

| Parameter | Default | Meaning |
| --- | --- | --- |
| `default_storage_limit` | `10737418240`, 10 GiB | Each user's limit, in bytes |
| `exempt_users_created_before` | none | A date, `"2026-01-01T00:00:00+00:00"`: users created before it have no limit, to bring quotas in for new users only |
| `cache_timeout` | `3600` | Seconds a user's storage stays cached at most. Every upload or deletion clears it already |

### Change one user's limit

In the Django admin, a user's **storage limit override (GB)** sets their limit
in gigabytes of 1000³ bytes, and `0` means unlimited. It wins over both
parameters above. To make unlimited everyone without an override who stores
more than a threshold, in the same gigabytes, run from a backend container:

```bash
python manage.py grant_unlimited_storage --threshold-gb 10 --dry-run
```

It lists the users it would change; run it again without `--dry-run` to change
them.

### Leave a file out of the quotas

A file another application creates through the
[external API](../../integrating/external-api.md#customise-created-item-attributes-per-audience)
can be left out of its creator's storage, per calling application.

## Writing your own backend

A backend is a class inheriting from
[`EntitlementsBackend`](https://github.com/suitenumerique/drive/blob/main/src/backend/core/entitlements/backends/base.py).
It answers two questions about a user, each with a dictionary holding a
`result` and, optionally, a `message` shown to the user:

```python
from core.entitlements.backends.base import EntitlementsBackend


class CustomEntitlementsBackend(EntitlementsBackend):
    def __init__(self, **kwargs):
        self.api_url = kwargs["api_url"]

    def can_access(self, user):
        # May this user sign in?
        return {"result": True}

    def can_upload(self, user):
        # May this user upload a file?
        return {"result": False, "message": "Uploads are disabled"}
```

Install it in the backend image, then name it, with the arguments its
constructor takes:

```bash title="Backend environment"
ENTITLEMENTS_BACKEND=your_module.backends.CustomEntitlementsBackend
ENTITLEMENTS_BACKEND_PARAMETERS={"api_url": "https://rules.example.com"}
```

Every method whose name starts with `can_` is also served to the signed-in user
at `GET /api/v1.0/entitlements/`, which the frontend reads:

```json
{
  "can_access": {"result": true},
  "can_upload": {"result": false, "message": "Upload quota exceeded"},
  "context": {}
}
```

The response also carries `quota` when the backend returns one.

Drive also ships `core.entitlements.backends.deploycenter.DeployCenterEntitlementsBackend`,
which asks a [DeployCenter](https://github.com/suiteterritoriale/deploycenter)
service. Its parameters are the arguments of its
[constructor](https://github.com/suitenumerique/drive/blob/main/src/backend/core/entitlements/backends/deploycenter.py).

Every setting of this page is under
[Storage quotas](../../reference/env-variables.md#storage-quotas) in the
variables reference.
