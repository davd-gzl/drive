# Merging accounts

One person can end up with two Drive accounts, after an email change for
instance. Drive merges them: the files, accesses, stars and sent invitations
of one account move to the other, and the emptied account is deactivated.

Drive has no form for users to ask for it. Collect the requests in a form of
your own, such as one made with Grist, export them as a CSV file, and import it
in the Django admin: **Core** › **User reconciliation CSV imports** ›
**Add user reconciliation CSV import**.

## The CSV file

| Column | Required | Holds |
| --- | --- | --- |
| `id` | Yes | A unique row ID, so a row already imported is skipped next time |
| `active_email` | Yes | The email of the account that stays |
| `inactive_email` | Yes | The email of the account merged into it, or several separated by `\|` |
| `active_email_checked` | No | `1` when your form already proved the person owns the active email, `0` by default |
| `inactive_email_checked` | No | The same, for the inactive emails |

## Process the requests

Importing the file creates one entry per row under **Core** ›
**User reconciliations**, and emails each address the form did not prove, to
confirm that the person owns it.

Once both sides are confirmed, an entry's status is `ready`. Select the entries
to merge, then run the action **Process selected user reconciliations**: it
merges the `ready` ones and skips the others.

## When a request fails

When an address of a request matches no account, Drive emails the person to say
so. Set [`USER_RECONCILIATION_FORM_URL`](../../reference/env-variables.md#USER_RECONCILIATION_FORM_URL)
to your form's address, and that email links it, so they can try again.

To try the whole flow locally, `make reconciliation-demo` creates demo accounts
and a CSV file to import.
