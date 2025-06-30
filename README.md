<div align="center">
 

  <h3 align="center">Corporate News Aggregator </h3>

  <p align="center">
	Full stack web application that aggregates news articles on companies relating to the ethics of their business
    <br />
    <a href="https://desa-thomas.github.io/"><strong>github.io link soon</strong></a>
    <br />
    <br />
    <a href="https://github.com/desa-thomas/controversy-aggregator/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/desa-thomas/controversy-aggregator/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

![Search page](/screenshots/searchpage_ss.png)
## About
**Corporate News Aggregator** is a full-stack web application focused on tracking and organizing news related to company ethics. It combines public company data from [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) with real-time news articles from [GNews](https://gnews.io/), categorized by ethical themes such as **labor**, **environment**, **privacy**, and **governance**.

The app retrieves:
- Company metadata (industry, logo, description) from Wikidata
- Relevant news articles from GNews based on [ethical categories](/backend/ethics_categories.py) 

This tool offers a convenient platform for:

- Researching corporate business practices
- Exploring industry-specific media coverage through an ethical lens

The frontend, built with JavaScript and HTML, is hosted on GitHub, while the backend — powered by Python (Flask) and MariaDB — runs on my Raspberry Pi at home.

🚧 _Note:_ The frontend and API are still under active development. Once stable, the app will be hosted publicly. In the meantime, you're welcome to:

- Browse the codebase
- View [screenshots](/screenshots)
- Or host the application locally by following the setup instructions
## Screenshots

![company page](/screenshots/resultspage_ss.png)
![category select dropdown menu](/screenshots/dropdown_ss.png)
### Built With
<div>
<img height="32" width="32" src="https://cdn.simpleicons.org/javascript" /> 
<img height="32" width="32" src="https://cdn.simpleicons.org/python" />
<img height="32" width="32" src="https://cdn.simpleicons.org/flask/black/white" />
<img height="32" width="32" src="https://cdn.simpleicons.org/mariadb" />
<img height="32" width="32" src="https://cdn.simpleicons.org/raspberrypi" />
</div>
And [GNews's](https://gnews.io/) API

## License

MIT License

Copyright (c) 2025 Thomas De Sa

See `LICENSE.md` for more details

## Contact

Thomas De Sa - desa2thomas@gmail.com

