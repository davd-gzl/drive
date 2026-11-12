# External API

Another application can act in Drive on behalf of a user: list their files,
create folders, upload, share. It calls `/external_api/v1.0/` with the access
token the user signed in to it with, and Drive checks that token with your
sign-in provider. In OpenID Connect's words, Drive is then a *resource server*.

Every route and its fields are in the [API reference](../reference/swagger.html),
under **External API**: it lists them all, and the `EXTERNAL_API` setting
decides which ones answer. The routes and their rules may still change between
versions.

## Turn it on

Register Drive at your provider as a client allowed to introspect tokens, then
set on the backend:

```bash title="Backend environment"
OIDC_RESOURCE_SERVER_ENABLED=True
OIDC_OP_URL=https://id.example.com/realms/drive
OIDC_OP_INTROSPECTION_ENDPOINT=https://id.example.com/realms/drive/protocol/openid-connect/token/introspect
OIDC_RS_CLIENT_ID=drive-resource-server
OIDC_RS_CLIENT_SECRET=<its secret>
OIDC_RS_ALLOWED_AUDIENCES=my-app
```

[`OIDC_RS_ALLOWED_AUDIENCES`](../reference/env-variables.md#OIDC_RS_ALLOWED_AUDIENCES)
lists the applications whose tokens Drive accepts, as named in the claim
[`OIDC_RS_AUDIENCE_CLAIM`](../reference/env-variables.md#OIDC_RS_AUDIENCE_CLAIM),
`client_id` by default. The token check comes from
[django-lasuite](https://github.com/suitenumerique/django-lasuite/blob/main/documentation/how-to-use-oidc-resource-server-backend.md).

## Customise allowed routes

Configure the `EXTERNAL_API` setting to control which routes and actions are available in the external API. Set it as the `EXTERNAL_API` environment variable, a Python dictionary. It replaces the whole default: a route left out is turned off, so copy every key you keep.

Default configuration:

```python
EXTERNAL_API = {
    "items": {
        "enabled": True,
        "actions": ["create", "list", "retrieve", "children", "upload_ended"],
    },
    "item_access": {
        "enabled": False,
        "actions": [],
    },
    "item_invitation": {
        "enabled": False,
        "actions": [],
    },
    "users": {
        "enabled": True,
        "actions": ["get_me"],
    }
}
```

**Endpoints:**

- `items`: Controls `/external_api/v1.0/items/`. Available actions: `list`, `retrieve`, `create`, `update`, `partial_update`, `destroy`, `children`, `upload_ended`, `move`, `restore`, `trashbin`, `hard_delete`, `tree`, `breadcrumb`, `link_configuration`, `favorite`, `media_auth`, `wopi`, `convert`, `favorite_list`, `recents`, `deletion_info`, `search`, `batch_share`, `unlock`, `restrict`, `leave`, `download`, `export`, `duplicate`
- `item_access`: Controls `/external_api/v1.0/items/{id}/accesses/`. Available actions: `list`, `retrieve`, `create`, `update`, `partial_update`, `destroy`
- `item_invitation`: Controls `/external_api/v1.0/items/{id}/invitations/`. Available actions: `list`, `retrieve`, `create`, `update`, `partial_update`, `destroy`
- `users`: Controls `/external_api/v1.0/users/`. Available actions: `list`, `get_me`, `contacts`, `update`, `partial_update`

Each endpoint has `enabled` (boolean) and `actions` (list of allowed actions). Only actions explicitly listed are accessible.

## Customise created item attributes per audience

The `EXTERNAL_API_AUD_ITEM_ATTRIBUTES` setting gives extra attributes to the
items each calling application creates, keyed by the application's name in
`OIDC_RS_AUDIENCE_CLAIM`. Set it as an environment variable, a Python
dictionary.

```python
EXTERNAL_API_AUD_ITEM_ATTRIBUTES = {
    "some_audience": {
        "quota_excluded": True,
    },
}
```

With this configuration, every item created by a request authenticated with the
`some_audience` audience is excluded from its creator's storage quota computation.
Audiences without an entry keep the default item attributes.

## Permissions

A request acts on behalf of the user identified by the access token. Drive checks that:

- The token holds at least one scope of `OIDC_RS_SCOPES`.
- The token audience is in `OIDC_RS_ALLOWED_AUDIENCES`.
- The action is listed in `EXTERNAL_API`, otherwise the API returns a 403. With `enabled: False`, the route does not exist and returns a 404.
- The user's role on the item allows the action, with the same rules as the main API.

There are no rights specific to the calling application, and scopes do not restrict actions.

### Roles

| Role | Rights |
|---|---|
| `reader` | Read |
| `editor` | Read, edit, and delete a non-root item they created |
| `administrator` | Read, edit, delete a non-root item, and share |
| `owner` | Same as `administrator`, and can delete a root item and grant or change the `owner` role |

A role is set on an item, either a file or a folder, and applies to its descendants. The access role is the highest one among the item and its ancestors. A link that reaches the user can raise it up to `link_role` (`reader` or `editor`), but never gives the right to share, see `link_configuration`.

`GET /external_api/v1.0/items/{id}/` returns the access role of the token's user in `user_role`, which ignores links, and the allowed actions in `abilities`, which take links into account. It does not require enabling `item_access`.

### Accesses

Accesses target existing users, through `/external_api/v1.0/items/{id}/accesses/`.

| Action | Rule |
|---|---|
| `list` | Any access role on the item, other users get an empty list. Accesses include those inherited from ancestors. Readers and editors only see administrators and owners. |
| `retrieve` | The access's own user, or an administrator or owner |
| `create` | Administrator or owner. The new role must be higher than the one the target user already has on the item or its ancestors, otherwise the API returns a 400. Sends an email to the target user. |
| `update`, `partial_update` | Administrator or owner. A role lower than the inherited one returns a 403. Setting the role inherited from ancestors deletes the explicit access and returns a 204. |
| `destroy` | Administrator or owner |

Only an owner can grant the `owner` role, or change or delete an owner access. The last owner of a root item cannot be changed or deleted.

### Invitations

Invitations target emails with no Drive account yet, through `/external_api/v1.0/items/{id}/invitations/`. All actions require an administrator or owner, except `list` which returns an empty list to other users. Only an owner can invite with the `owner` role. Creating an invitation for the email of a registered user returns a 400, unless `OIDC_ALLOW_DUPLICATE_EMAILS` is enabled.

## Call Drive

The calling application signs its users in through the same provider, keeps
their access token, and sends it to Drive's `/external_api/v1.0/` routes.
django-lasuite's guide to
[calling a resource server](https://github.com/suitenumerique/django-lasuite/blob/main/documentation/how-to-use-oidc-call-to-resource-server.md)
sets that up for a Django application. The examples below are views of such an
application.

### Upload a file

This view of the calling application uploads a file to the root of the user's
Drive. `DRIVE_API` is the calling application's own setting, such as
`https://drive.example.com/external_api/v1.0`.

```python
import os

import requests
from django.conf import settings
from django.utils.decorators import method_decorator
from lasuite.oidc_login.decorators import refresh_oidc_access_token
from rest_framework.response import Response


@method_decorator(refresh_oidc_access_token)
def upload_file(self, request):
    """Upload sample.txt to the root of the user's Drive."""
    access_token = request.session.get("oidc_access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    path = os.path.join(os.path.dirname(__file__), "sample.txt")

    # Create the file with its size: Drive answers with an upload address
    response = requests.post(
        f"{settings.DRIVE_API}/items/",
        json={"type": "file", "filename": "sample.txt", "size": os.path.getsize(path)},
        headers=headers,
    )
    response.raise_for_status()
    item = response.json()

    # Send the file to that address. The ACL must equal Drive's
    # AWS_S3_UPLOAD_ACL, private by default; leave it out when that is "default"
    with open(path, "rb") as f:
        upload = requests.put(
            item["policy"],
            data=f.read(),
            headers={"Content-Type": "text/plain", "x-amz-acl": "private"},
        )
    upload.raise_for_status()

    # Tell Drive the upload ended
    response = requests.post(
        f"{settings.DRIVE_API}/items/{item['id']}/upload-ended/",
        json={},
        headers=headers,
    )
    response.raise_for_status()
    return Response(response.json())
```

### Create a new folder

Create a folder at the root with `POST items/`, or inside a folder with
`POST items/{id}/children/`:

```python
response = requests.post(
    f"{settings.DRIVE_API}/items/{parent_id}/children/",
    json={"type": "folder", "title": "My folder"},
    headers=headers,
)
```

### Share an item

In `EXTERNAL_API`, enable `item_access` and `item_invitation` with the `create` action, and add `list` to `users`. The user search tolerates typos in emails, so compare the returned email with the expected one before sharing. It only returns active users: the invitation returns a 400 for the email of an inactive account, unless `OIDC_ALLOW_DUPLICATE_EMAILS` is enabled.

```python
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
email = "colleague@example.com"

response = requests.get(f"{settings.DRIVE_API}/users/", params={"q": email}, headers=headers)
response.raise_for_status()
user = next((user for user in response.json() if user["email"] == email), None)

if user:
    # Give an access to an existing user
    response = requests.post(
        f"{settings.DRIVE_API}/items/{item['id']}/accesses/",
        json={"user_id": user["id"], "role": "editor"},
        headers=headers,
    )
else:
    # Invite an email with no account yet
    response = requests.post(
        f"{settings.DRIVE_API}/items/{item['id']}/invitations/",
        json={"email": email, "role": "editor"},
        headers=headers,
    )
response.raise_for_status()
```

### Get user information

`users/me/` returns the signed-in user:

```python
response = requests.get(f"{settings.DRIVE_API}/users/me/", headers=headers)
```
