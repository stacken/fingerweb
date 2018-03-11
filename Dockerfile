FROM python:3

RUN adduser --no-create-home --gecos FALSE --disabled-password finger

ENV PYTHONUNBUFFERED 1

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD . /app
WORKDIR /app

RUN chown -R finger:finger /app
USER finger

CMD bash -c '\
	/app/manage.py migrate && \
	/app/manage.py runserver 0.0.0.0:8000 \
	'
