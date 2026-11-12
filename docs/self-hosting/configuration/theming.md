# Look and feel

Drive's colours, footer and links change through backend settings, which the
browser reads at each page load: no rebuild is needed. A restart of the backend
applies a changed variable, and a changed footer file shows within a day,
[`THEME_CUSTOMIZATION_CACHE_TIMEOUT`](../../reference/env-variables.md#THEME_CUSTOMIZATION_CACHE_TIMEOUT).

## Colours

[`FRONTEND_THEME`](../../reference/env-variables.md#FRONTEND_THEME) picks one
of the built-in themes: `default`, `dark`, `dsfr-light`, `dsfr-dark`,
`anct-light` or `anct-dark`.

For anything further, [`FRONTEND_CSS_URL`](../../reference/env-variables.md#FRONTEND_CSS_URL)
loads a stylesheet of yours after Drive's own:

```css title="custom-style.css"
body {
  background-color: #3498db;
}
```

## Your own script

[`FRONTEND_JS_URL`](../../reference/env-variables.md#FRONTEND_JS_URL) loads a
script of yours in every page, to add an element or call a service. It runs
with the signed-in user's rights, so serve it from a place only you can change.

## The footer

The footer of the home page reads a JSON file:
[the default one](https://github.com/suitenumerique/drive/blob/main/src/backend/drive/configuration/theme/default.json)
shows its shape. Under `footer`, the `default` block applies to every language
and a block per language code, `en` or `fr`, adds to it or replaces its parts:

```json title="theme.json"
{
  "footer": {
    "default": {
      "externalLinks": [
        {"label": "Our website", "href": "https://example.com"}
      ]
    },
    "en": {
      "legalLinks": [
        {"label": "Legal notice", "href": "https://example.com/legal"}
      ]
    }
  }
}
```

Point [`THEME_CUSTOMIZATION_FILE_PATH`](../../reference/env-variables.md#THEME_CUSTOMIZATION_FILE_PATH)
at your file. With the Helm chart, write the content as YAML under
`backend.themeCustomization.file_content`, not as a JSON string, and set
`backend.themeCustomization.enabled` to `true`: the chart writes it out as
JSON in place of the default file.

## Links and menus

| To | Set |
| --- | --- |
| Add a help menu to the sidebar, with documentation, support and legal links | [`FRONTEND_HELP_MENU_CONFIG`](../../reference/env-variables.md#FRONTEND_HELP_MENU_CONFIG) |
| Send the home page's visitors to your own page | [`FRONTEND_EXTERNAL_HOME_URL`](../../reference/env-variables.md#FRONTEND_EXTERNAL_HOME_URL) |
| Set the home page's **Learn more** link | [`FRONTEND_MORE_LINK`](../../reference/env-variables.md#FRONTEND_MORE_LINK) |
| Hide the menu of La Suite's other apps | [`FRONTEND_HIDE_GAUFRE`](../../reference/env-variables.md#FRONTEND_HIDE_GAUFRE) |
| Hide the **What's new** window | [`FRONTEND_RELEASE_NOTE_ENABLED`](../../reference/env-variables.md#FRONTEND_RELEASE_NOTE_ENABLED) |
| Add a **Give feedback** button | [`FRONTEND_FEEDBACK_BUTTON_SHOW`](../../reference/env-variables.md#FRONTEND_FEEDBACK_BUTTON_SHOW) |

The emails Drive sends have their own logos, font and links: they are under
[Email](../../reference/env-variables.md#email) in the variables reference.
