# Fingerweb

This is the sources for Stackens member system called Fingerweb. Fingerweb is a Django application that manages member data, accounts and various member related tasks.

## Features

### Member database

The master copy of our member data is still managed inside `finger.json`, this system expect the database to be refreshed with `./manage.py readjson --file finger.json`. Once a day or so, the system expects `./manage.py updatedb` to be executed, this runs batch operations against the database.

### Member login

Active members can use the system to login and inspect some of their member data, request service accounts and do some other minor tasks.

### Service management

Fingerweb manages account creation to some of Stackens systems. The tool is build around the idea of self service for members. Administrators can create services inside Django Admin, users can then request access to the systems in question. The actual systems will then use a REST API to integrate and sync state with fingerweb.

### Administrative system for the Board

The member database can be browsed and filtered inside Django Admin where a Board member can:

* Search and filter to find and inspect members
* Modify membership data
* Generate reports like membership lists
* Send e-mail to members based on templates or just plain text

## Development

### How to run it with Docker

There is an included `docker-compose.yml` that should get you started. This include a Postgres database and a dummy e-mail server to debug the email function. This is a easy way to get started, with a production like environment:

```
docker-compose up --build
```

### Run manage.py inside the containers

This example will enter a running container and run manage.py.

```
docker-compose exec fingerweb /app/manage.py makemigrations
```

### Import data

The folder `import` will be mounted to `/import` inside the container,
so for example to import `finger.json` do this:

```
cp $FINGER_FILE import/finger.json
docker-compose exec fingerweb /app/manage.py readjson --file /import/finger.json
```

## Run Django outside Docker

Sometimes it can be easier to run the application directly on the host.

```
virtualenv -p python3 .env
. .env/bin/activate
export SECRET_KEY=none
export ALLOWED_HOSTS=127.0.0.1,localhost
export DEBUG=True
export DATABASE_URL=sqlite:///db.sqlite3
export DJANGOADMIN_PASSWORD=password
./manage.py
```

## Run tests

If you are working locally:

``` python
pip install pytest-django
pytest
```

## Production build

After a merge to master, a webhook will fire and the Dockerfile will be built, deployed and started on the production server.
