FROM python:3.12-slim

RUN apt-get update -y
RUN apt-get install -y git gdal-bin python3-gdal build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

WORKDIR /code
COPY requirements /code/requirements
RUN pip install -r requirements/development.txt --no-cache-dir

EXPOSE 8001

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "apps.asgi:application"]



