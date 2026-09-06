## Deployment
HAME is deployed at https://hame-kf72.onrender.com using Render's free plan. Due to the limitations of the free plan, it may take 30-60 seconds for the site to load if it has had no activity recently.  
Please be aware that Render's free PostgreSQL server is only available for 30 days from its creation, so the database behind HAME will be deactivated on 26th September 2026 and the deployed application will no longer be functional. 

## AI use declaration
Predominantly user written, Claude used in debugging:
|      File       |             Description            |
| --------------- | ---------------------------------- |
| about.html      | Docs & explanation of app          |
| add_review.html | Review page                        |
| base.html       | Base Django template               |
| index.html      | Home page - map & location display |
| login.html      | Login page                         |
| profile.html    | User profile page                  |
| register.html   | Account creation page              |
| forms.py        | Account creation and review forms  |
| models.py       | Defines database structure         | 
| urls.py (both)  | Defines url scheme                 |

Predominantly AI assisted (Claude):
|      File       |             Description            |
| --------------- | ---------------------------------- |
| views.py        | Connects backend to templates      |
| styles.css      | Customising beyond Bootstrap       |
| test_auth.py    | Authentication tests               |
| test_models.py  | Model/database tests               |
| test_reviews.py | Review tests                       |
| seed_db.py      | Formats raw OSM data for Postgres  |


