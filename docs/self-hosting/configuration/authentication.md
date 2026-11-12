# Sign-in

Users have no Drive password: they sign in through an
[OpenID Connect](https://openid.net/developers/how-connect-works/) provider,
such as Keycloak, ProConnect or any other compliant one. Drive creates each
user's account the first time they sign in.

## Register Drive with your provider

Create a confidential client for Drive at your provider, with these addresses,
`drive.example.com` being your Drive domain:

| Setting at the provider | Value |
| --- | --- |
| Redirect URI | `https://drive.example.com/api/v1.0/callback/` |
| Post-logout redirect URI | `https://drive.example.com/api/v1.0/logout-callback/` |
| Scopes | `openid email`, plus whatever gives the user's name |

The provider gives you a client ID and a secret.

## Point Drive at it

Set these on the backend, with your provider's addresses: most providers list
them at `/.well-known/openid-configuration`.

```bash title="Backend environment"
OIDC_OP_AUTHORIZATION_ENDPOINT=https://id.example.com/realms/drive/protocol/openid-connect/auth
OIDC_OP_TOKEN_ENDPOINT=https://id.example.com/realms/drive/protocol/openid-connect/token
OIDC_OP_USER_ENDPOINT=https://id.example.com/realms/drive/protocol/openid-connect/userinfo
OIDC_OP_JWKS_ENDPOINT=https://id.example.com/realms/drive/protocol/openid-connect/certs
OIDC_OP_LOGOUT_ENDPOINT=https://id.example.com/realms/drive/protocol/openid-connect/logout
OIDC_RP_CLIENT_ID=drive
OIDC_RP_CLIENT_SECRET=<the client secret>
LOGIN_REDIRECT_URL=https://drive.example.com
LOGIN_REDIRECT_URL_FAILURE=https://drive.example.com
LOGOUT_REDIRECT_URL=https://drive.example.com
OIDC_REDIRECT_ALLOWED_HOSTS=drive.example.com
```

The addresses above follow Keycloak's layout, with a realm named `drive`.

## Names and accounts

Drive shows the name it builds from the claims named in
[`OIDC_USERINFO_FULLNAME_FIELDS`](../../reference/env-variables.md#OIDC_USERINFO_FULLNAME_FIELDS),
`first_name` and `last_name` unless you change them. A provider sending
`given_name` and `family_name` needs
`OIDC_USERINFO_FULLNAME_FIELDS=given_name,family_name` and
`OIDC_USERINFO_SHORTNAME_FIELD=given_name`.

A user is recognised by the provider's identifier, the `sub` claim. When a
`sub` is new, Drive looks for an account with the same email and signs the user into it,
unless
[`OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION`](../../reference/env-variables.md#OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION)
is `False`. That lets people keep their files when you change provider, as long
as their email stays the same.

Drive refuses a sign-in only when the provider sends no `sub`. To decide who
may sign in by your own rules, write an entitlements backend, as
[Storage quotas](quotas.md#writing-your-own-backend) shows.

Every setting of this page, and the less common ones, are under
[Sign-in](../../reference/env-variables.md#sign-in) in the variables reference.
