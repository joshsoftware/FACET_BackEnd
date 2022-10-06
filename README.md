# FACET (Backend)

### Prerequisites:
- Postgres
- Python 3.8


## How to run locally?


Step 1: 

Clone the repository:
```
git clone https://github.com/joshsoftware/FACET_BackEnd.git
```

Go to root folder and install requirements.txt
```
pip install -r requirements.txt
```

Step 2: Create A Database

Create a databse in postgres named facetdb using following commands:

Log in to an interactive Postgres session:
```
sudo -u postgres psql
```

Create a database:
```
CREATE DATABASE facetdb;
```

Next, create a database user for our project:
```
CREATE USER username WITH PASSWORD 'password';
```

Then give this new user access to administer your new database:
```
GRANT ALL PRIVILEGES ON DATABASE facetdb TO username;
```

Step 3: Add environment variables

Open .env.local and add DATABASE_URL in form of:
```
postgresql://username:password@localhost:5432/facetdb
```

Note: If your password have special character then uri must be in encode form. For ex. If password is 'pass@123' then it should be 'pass%40123'.

step 4: Migrate db

Set flask app in terminal
```
export FLASK_APP=run.py
```

Migrate and upgrade db
```
flask db init
flask db migrate
flask db upgrade
```

Step 5: Run app

To run application use following command:
```
flask run
```
