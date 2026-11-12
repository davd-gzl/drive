<p align="center">
  <a href="https://github.com/suitenumerique/drive">
    <img alt="Drive banner" src="/docs/assets/banner-drive.png" width="100%" />
  </a>
</p>
<p align="center">
  <img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/suitenumerique/drive"/>
  <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed/suitenumerique/drive"/>
  <a href="https://github.com/suitenumerique/drive/blob/main/LICENSE">
    <img alt="GitHub closed issues" src="https://img.shields.io/github/license/suitenumerique/drive"/>
  </a>
  <a href="https://digitalpublicgoods.net/r/la-suite-drive-collaborative-file-sharing">
    <img src="https://img.shields.io/badge/Verified-DPG-3333AB?logo=data:image/svg%2bxml;base64,PHN2ZyB3aWR0aD0iMzEiIGhlaWdodD0iMzMiIHZpZXdCb3g9IjAgMCAzMSAzMyIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTE0LjIwMDggMjEuMzY3OEwxMC4xNzM2IDE4LjAxMjRMMTEuNTIxOSAxNi40MDAzTDEzLjk5MjggMTguNDU5TDE5LjYyNjkgMTIuMjExMUwyMS4xOTA5IDEzLjYxNkwxNC4yMDA4IDIxLjM2NzhaTTI0LjYyNDEgOS4zNTEyN0wyNC44MDcxIDMuMDcyOTdMMTguODgxIDUuMTg2NjJMMTUuMzMxNCAtMi4zMzA4MmUtMDVMMTEuNzgyMSA1LjE4NjYyTDUuODU2MDEgMy4wNzI5N0w2LjAzOTA2IDkuMzUxMjdMMCAxMS4xMTc3TDMuODQ1MjEgMTYuMDg5NUwwIDIxLjA2MTJMNi4wMzkwNiAyMi44Mjc3TDUuODU2MDEgMjkuMTA2TDExLjc4MjEgMjYuOTkyM0wxNS4zMzE0IDMyLjE3OUwxOC44ODEgMjYuOTkyM0wyNC44MDcxIDI5LjEwNkwyNC42MjQxIDIyLjgyNzdMMzAuNjYzMSAyMS4wNjEyTDI2LjgxNzYgMTYuMDg5NUwzMC42NjMxIDExLjExNzdMMjQuNjI0MSA5LjM1MTI3WiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+Cg==" alt="DPG Badge"/>
  </a>    
</p>

<p align="center">
  <a href="https://matrix.to/#/#drive-official:matrix.org">
    Chat on Matrix
  </a> - <a href="docs/index.md">
    Documentation
  </a> - <a href="docs/self-hosting/index.md">
    Self-hosting
  </a> - <a href="mailto:drive@numerique.gouv.fr">
    Reach out
  </a>
</p>

# La Suite Drive: Collaborative File Sharing

**LaSuite Drive, where your files become collaborative assets through seamless teamwork.**

<img src="/docs/assets/Drive_screenshot.png" width="100%" align="center"/>

LaSuite Drive is an open-source tool focused on file storage, editing and sharing with granular access control.

## Features

- Upload files and whole folders, by drag and drop or from the Import button
- Preview PDFs, images, audio and video in the browser
- Edit office documents online through Collabora or OnlyOffice, over WOPI
- Share a file or a folder with people, each with their own role, and with a
  link
- Invite people by email before they have an account
- Trash with restore, malware scanning of uploads, storage quotas
- A file picker other apps can embed

## Documentation

The [documentation](docs/index.md) has a part for each reader:

- **People using Drive**: [Getting started](docs/user/getting-started.md),
  [Sharing](docs/user/sharing.md),
  [Finding and organising files](docs/user/organising.md)
- **Administrators**: [Self-hosting](docs/self-hosting/index.md),
  [Install on Kubernetes](docs/self-hosting/kubernetes.md),
  [Environment variables](docs/reference/env-variables.md)
- **Developers**: [How Drive works](docs/overview/how-drive-works.md),
  [External API](docs/integrating/external-api.md),
  [Develop locally](docs/contributing/develop.md)

Build it as a website with [Zensical](https://zensical.org/):

```bash
uvx zensical serve
```

### Known instances

| URL | Organisation | Access |
| --- | --- | --- |
| [fichiers.numerique.gouv.fr](https://fichiers.numerique.gouv.fr/) | DINUM | French central administration, through ProConnect |
| [fichiers.suite.anct.gouv.fr](https://fichiers.suite.anct.gouv.fr/) | ANCT | French local administration, through ProConnect |
| [fichiers.lasuite.coop](https://fichiers.lasuite.coop/) | lasuite.coop | Free demo open to all, reset after a month |
| [mosa.cloud](https://mosa.cloud/) | mosa.cloud | A Dutch company offering La Suite apps |

Run one too? Open a pull request adding it.

## Contributing 🙌

This project is community-driven and PRs are welcome. Do not hesitate to get in touch if you have any question related to our implementation or design decisions. We <3 contributions of any kind, big and small :

- [Contribution guide](https://github.com/suitenumerique/drive/blob/main/CONTRIBUTING.md)
- [Translations](https://crowdin.com/project/lasuite-drive)
- [Chat with us!](https://matrix.to/#/#drive-official:matrix.org)
- Open a PR (see our instructions on [developing La Suite Drive locally](docs/contributing/develop.md))
- Submit a [feature request](https://github.com/suitenumerique/drive/issues/new?assignees=&labels=enhancement&template=Feature_request.md) or [bug report](https://github.com/suitenumerique/drive/issues/new?assignees=&labels=bug&template=Bug_report.md)

#### Gov ❤️ open source

All features we develop will always remain open-source.
Come help us make LaSuite Drive even better. We're growing fast and would love some help. We are always looking for new partners, feel free to [contact us](mailto:fichiers@numerique.gouv.fr) if you are interested in using or contributing to LaSuite Drive. 

## Roadmap

Curious where LaSuite Drive is headed?
Explore upcoming features, priorities and long-term direction on our [public roadmap](https://docs.numerique.gouv.fr/docs/eacaabdb-d92b-465d-bedf-75d28b397221/).

## License

This work is released under the MIT License (see [LICENSE](./LICENSE)).

While LaSuite Drive is a public driven initiative our licence choice is an invitation for private sector actors to use, sell and contribute to the project.

## Credits

LaSuite Drive is built on top of [Django Rest Framework](https://www.django-rest-framework.org/), [Next.js](https://nextjs.org/). We thank the contributors of all these projects for their awesome work!
