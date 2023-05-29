# KeyMG

## Project Layout 

We will divide our app in below components, according to [Flask recommended layout](https://flask.palletsprojects.com/en/2.1.x/tutorial/layout/) and [Skeleton Minimal Architecture](https://laymanclass.com/how-to-structure-flask-application-for-larger-projects/):


    keymg
    │
    ├── database/
    ├── keymg
    │   ├── __init__.py
    │   ├── extensions.py
    │   ├── routes.py
    │   ├── controllers.py
    │   ├── service/
    │   ├── domain/
    │   │
    │   └── ui
    │       ├── static
    │       │   ├── css
    │       │   │   └── styles.css
    │       │   ├── img
    │       │   └── js
    │       │       └── app.js
    │       └── templates
    │           ├── index.html
    │           └── search.html
    │
    ├── wsgi.py
    ├── .gitignore
    ├── requirements.txt
    └── README.md