# Online editing

Drive opens text documents, spreadsheets and presentations in an online office
editor, [Collabora Online](https://www.collaboraonline.com/) or
[OnlyOffice Docs](https://www.onlyoffice.com/docs). It talks to them through
[WOPI](https://learn.microsoft.com/en-us/microsoft-365/cloud-storage-partner-program/online/),
a protocol where the editor fetches and saves the file through Drive's API.
Without an editor, those files can still be uploaded, shared and downloaded.

## Connect an editor

Run the editor on its own domain, then set on the backend:

```bash title="Backend environment"
WOPI_CLIENTS=collabora
WOPI_COLLABORA_DISCOVERY_URL=https://office.example.com/hosting/discovery
WOPI_SRC_BASE_URL=https://drive.example.com
```

- [`WOPI_CLIENTS`](../../reference/env-variables.md#WOPI_CLIENTS) lists the
  editors, `collabora`, `onlyoffice` or both.
- Each one listed needs its `WOPI_<NAME>_DISCOVERY_URL`, the editor's
  `/hosting/discovery` address: the backend refuses to start without it.
- [`WOPI_SRC_BASE_URL`](../../reference/env-variables.md#WOPI_SRC_BASE_URL) is
  Drive's address as the editor reaches it.

The editor must accept Drive's backend as a WOPI host: on Collabora's
container, set the `aliasgroup1` variable to the host of `WOPI_SRC_BASE_URL`.

## Load the editors' file types

Drive reads which file types each editor opens from its discovery address, in
a background task a Celery worker runs. The `trigger_wopi_configuration`
command queues that task, and Celery beat queues it again once a day, at 3:00
UTC by default. Run the command once after setting the variables: the Helm
chart's `configure-wopi` job runs it, and by hand it is
`python manage.py trigger_wopi_configuration` in a backend container.

Images and PDFs never open in an editor, since Drive's own viewer shows them:
[`WOPI_EXCLUDED_EXTENSIONS`](../../reference/env-variables.md#WOPI_EXCLUDED_EXTENSIONS)
and [`WOPI_EXCLUDED_MIMETYPES`](../../reference/env-variables.md#WOPI_EXCLUDED_MIMETYPES)
hold that list.

## Convert old Microsoft Office files

OnlyOffice can convert `.doc`, `.xls` and `.ppt` files to their current
formats: users then see **Convert to open this file**, and Drive saves the
converted copy beside the original. It needs OnlyOffice's JWT secret and its
conversion service:

```bash title="Backend environment"
WOPI_ONLYOFFICE_OPTIONS={"ForceConvertExtensions": ["doc", "xls", "ppt"], "ConvertServiceUrl": "https://office.example.com/converter"}
WOPI_ONLYOFFICE_CONVERT_JWT_SECRET=<OnlyOffice's JWT secret>
```

`ForceConvertExtensions` lists the extensions that must be converted before
they open.

## Who can edit

A user with the **Editor** role or above edits the file; a **Reader** opens it
read-only. Drive does not open a file still being scanned for malware, except
for the person who uploaded it, nor a file the scan found suspicious.

Every setting of this page is under
[Online editing](../../reference/env-variables.md#online-editing) in the
variables reference.
