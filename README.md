# fingerweb

A web app that might replace finger.{txt,json}.
The first usefull thing it might do is handle service-specific passwords
for some other web apps.

## Local Docker build

Possible you need to append sudo in front of `docker`, or become a member of the docker group.

Build a image called fingerweb:

`$ docker build -t fingerweb .`

Run the image, append the environment and map the port to the host:

```
$ docker run -ti \
  -e SECRET_KEY=none \
  -e ALLOWED_HOSTS=127.0.0.1,localhost \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e DEBUG=True \
  -e DJANGOADMIN_PASSWORD=password \
  -p 8080:8080 \
  fingerweb
```

With this you will end up with a clean environment, every time. If you like to keep
the database between runs, I recommend that you spins up a separate database container
and link then together, for example:

```
$ docker run -d \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=fingerweb \
  -e POSTGRES_PASSWORD=dbpassword \
  --name fingerwebdb \
  postgres:10
$ docker run -ti \
  --link fingerwebdb \
  -e SECRET_KEY=none \
  -e ALLOWED_HOSTS=127.0.0.1,localhost \
  -e DATABASE_URL=psql://postgres:dbpassword@fingerwebdb:5432/fingerweb \
  -e DEBUG=True \
  -e DJANGOADMIN_PASSWORD=password \
  -p 8080:8080 \
  fingerweb
```

## Production build

A image is built and published to Docker Hub at `stacken/fingerweb:tag` where
tag is `latest` for the master branch, and otherwise the branch name.

https://hub.docker.com/r/stacken/fingerweb/

After a merge to master, `stacken/fingerweb:latest` will be built and a webhook
will restart the production image.
