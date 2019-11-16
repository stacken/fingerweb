# fingerweb

A web app that might replace finger.{txt,json}.
The first usefull thing it might do is handle service-specific passwords
for some other web apps.

## How to run it with Docker

There is an included `docker-compose.yml` that should get you started.
This setup is somewhat similar to the production build.

Type `docker-compose up` to start the containers.

### Run manage.py inside the containers

This example will enter a running container and run manage.py.

```
docker-compose exec fingerweb /app/manage.py makemigrations
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

## Production build

A image is built and published to Docker Hub at `stacken/fingerweb:tag` where
tag is `latest` for the master branch, and otherwise the branch name.

https://hub.docker.com/r/stacken/fingerweb/

After a merge to master, `stacken/fingerweb:latest` will be built and a webhook
will restart the production image.
