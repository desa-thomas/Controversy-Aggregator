# Server Setup
1. Get API key from [GNEWS](https://gnews.io/)
2. Download, setup, and host [MariaDB](https://mariadb.org/) server
3. Create a `config.py` in `/backend` and `/backend/util` directories.
4. In `config.py` create variables `API_KEY`, `db_host`, `db_user`, `db_pass`, `db_name`
5. Uncomment main function in `/backend/util/database_setup.py` and run the script to populate database with company data
6. Run `server.py`, in debug mode with flask or production with waitress, to serve the API
7. Use the following endpoint to access the API: 
    - `URL/search?query=query` to search for company in database, returns 5 results. TODO: add param to adjust the # of results
    - `URL/company/company_name` to get data on `company_name` in database. Returns an error if `company_name` is not present in database
    - `URL/articles?company=&page=&category=`, where company, and page are required, and category is either empty or a category from `ETHICS_CATEGORIES`