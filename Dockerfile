FROM python:3

EXPOSE 8000

ENV PYTHONUNBUFFERED 1
ARG SECRET_KEY=none
ARG ALLOWED_HOSTS=localhost
ARG DATABASE_URL=sqlite:///db.sqlite3

RUN adduser --no-create-home --gecos FALSE --disabled-password finger \
	&& apt-get update \
	&& apt-get -y install ruby-sass nginx

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY manage.py /app/
COPY finger /app/finger/
COPY fingerweb /app/fingerweb/
COPY services /app/services/
WORKDIR /app

RUN /app/manage.py migrate \
	&& /app/manage.py compilestatic \
	&& yes yes | /app/manage.py collectstatic \
	&& rm /app/*.sqlite3 \
	&& rm /app/*.txt \
	&& apt-get -y autoremove \
	&& rm -rf /var/lib/apt/lists/* \
	&& chown -R finger:finger /app /var/log/nginx /var/lib/nginx

ADD nginx-host.conf /etc/nginx/nginx.conf

USER finger

CMD bash -c '\
	/app/manage.py migrate && \
	nginx -c /etc/nginx/nginx.conf & \
	exec gunicorn fingerweb.wsgi:application \
		--bind 0.0.0.0:8000 \
		--workers 3 \
	'
