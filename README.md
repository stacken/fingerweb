# fingerweb

A web app that might replace finger.{txt,json}.
The first usefull thing it might do is handle service-specific passwords
for some other web apps.

To run in development mode, first make sure you have a (virtual) env with
the required packages installed:

```
pip install -r requirements.txt
```

In development mode, a sqlite database is used.  It is created by applying
the migrations:

```
./manage.py migrate
```

Then the server can be started:

```
./manage.py runserver
```
