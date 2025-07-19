# LabREI Microgrid Monitoring System — Environment Variables

This project uses a `.env` file to manage configuration.  
**Do not commit the file with real credentials to public repositories.**

## Variable reference

| Variable                 | Description                                                           | Example/Notes                   |
|--------------------------|-----------------------------------------------------------------------|---------------------------------|
| POSTGRES_DB              | Main database name for the system                                     | labrei_microgrid                |
| POSTGRES_USER            | Admin username for PostgreSQL                                         | labrei_admin                    |
| POSTGRES_PASSWORD        | Admin password for PostgreSQL                                         | YOUR_STRONG_PASSWORD            |
| PGADMIN_DEFAULT_EMAIL    | Admin email for pgAdmin web interface                                 | admin@le27.lab                  |
| PGADMIN_DEFAULT_PASSWORD | Admin password for pgAdmin                                            | adminLE27                       |
| DB_HOST                  | Database host for backend (Docker service name recommended: postgres) | postgres                        |
| DB_PORT                  | Database port (default PostgreSQL: 5432)                              | 5432                            |
| DB_NAME                  | Database name for backend connection                                  | labrei_microgrid                |
| DB_USER                  | Database user for backend connection                                  | labrei_admin                    |
| DB_PASSWORD              | Password for backend database connection                              | YOUR_STRONG_PASSWORD            |
| API_TITLE                | API documentation title                                               | LabREI Microgrid API            |
| API_VERSION              | API version                                                           | 1.0.0                           |
| API_DOCS_ENABLED         | Enables API documentation                                             | true                            |
| API_SECRET_KEY           | Secret key for JWT/session/authentication                             | change_this_secret              |
| REACT_APP_API_URL        | Backend API URL for the frontend (if used)                            | http://localhost:8000           |

**Note:**  
Make sure to set secure values for passwords and secrets before deploying to production!
