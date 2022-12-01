
#
# Launch a build container so we do not need to care about junk in the production image
#
FROM python:3.8 AS build

# This is needed to start the Django app
ARG SECRET_KEY=none
ARG ALLOWED_HOSTS=localhost
ARG DATABASE_URL=sqlite:///db.sqlite3

# Install sass
RUN apt-get update
RUN apt-get -y install ruby-sass

# Deploy files and install requirements
ADD app/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD app /app
RUN touch /app/.env
RUN mkdir /app/logs
WORKDIR /app

# Migrate (needed) and compile the static assets
RUN /app/manage.py migrate
RUN /app/manage.py compilestatic
RUN /app/manage.py collectstatic --noinput

# Clean up junk
RUN find /app -type f -name *.pyc -delete
RUN find /app -type d -name __pycache__ -delete
RUN find /app -type d -name .sass-cache -exec rm -rf {} \; || :
RUN rm db.sqlite3

#
# The production container
#
FROM python:3.8
EXPOSE 8080

COPY --from=build /app /app

RUN apt-get update \
	&& apt-get -y install nginx ruby-sass \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install -r /app/requirements.txt
WORKDIR /app

RUN adduser --no-create-home --gecos FALSE --disabled-password finger \
	&& sed -i "s/XXX_BUILD_DATE_XXX/`date +'%F %T'`/" /app/fingerweb/settings.py \
	&& chown -R finger:finger /app

ADD conf/nginx.conf /etc/nginx/nginx.conf
ADD entrypoint.sh /app/entrypoint.sh

CMD /app/entrypoint.sh
