# Full-text search

Drive searches file and folder names by itself. To search the text inside
files too, it sends them to [Find](https://github.com/suitenumerique/find),
La Suite's search service, and asks Find when a user searches.

## Register Drive in Find

In [Find](https://github.com/suitenumerique/find), create a service for Drive,
named `drive`, with the client ID Drive's users sign in through, `drive` by
default. Find gives the service a token, which Drive sends with each file.

## Point Drive at Find

```bash title="Backend environment"
SEARCH_INDEXER_CLASS=core.services.search_indexers.SearchIndexer
SEARCH_INDEXER_URL=https://find.example.com/api/v1.0/documents/index/
SEARCH_INDEXER_QUERY_URL=https://find.example.com/api/v1.0/documents/search/
SEARCH_INDEXER_SECRET=<the token Find gave the service>
```

From then on, Drive sends each file to Find when it is created or changed.
Only text files are read, up to 2 MB each.
[`SEARCH_INDEXER_CONTENT_MAX_SIZE`](../../reference/env-variables.md#SEARCH_INDEXER_CONTENT_MAX_SIZE)
changes the size, and
[`SEARCH_INDEXER_ALLOWED_MIMETYPES`](../../reference/env-variables.md#SEARCH_INDEXER_ALLOWED_MIMETYPES)
can only narrow the types: Drive extracts text from `text/*` files alone.

## Let searches reach Find

A search goes to Find with the user's own sign-in token, so Drive must keep it
in the session and renew it:

```bash title="Backend environment"
OIDC_STORE_ACCESS_TOKEN=True
OIDC_STORE_REFRESH_TOKEN=True
OIDC_STORE_REFRESH_TOKEN_KEY=<32 random bytes, URL-safe base64>
```

This command makes a valid key:

```bash
openssl rand -base64 32 | tr '+/' '-_'
```

## Index the existing files

Files uploaded before Find was connected are not in it yet. Send them all
once, from a backend container:

```bash
python manage.py index
```

Every setting of this page is under
[Search](../../reference/env-variables.md#search) in the variables reference.
