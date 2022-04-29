FROM python:3.7

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/djangoapp/src

COPY Pipfile Pipfile.lock /opt/services/djangoapp/src/
WORKDIR /opt/services/djangoapp/src
RUN pip install pipenv && pipenv install --system

COPY . /opt/services/djangoapp/src

EXPOSE 8000

CMD [ "gunicorn", \
    "--chdir", "app", "app.wsgi:application", \
    "-b", "0.0.0.0:8000", \
    "-c", "config/gunicorn/conf.py" ]