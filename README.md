# Project VIS Extension

This project has many dependencies. But you don't need to start over again on your workstation. The only thing you need to do is make sure you have installed Docker. Check out Docker's [documentation](https://docs.docker.com/install/) if your workstation doesn't have it. Docker Compose is recommended to reuse `docker-compose.yml`, you can install it by following its  [documentation](https://docs.docker.com/compose/install/).

It also includes necessary entry point files and automatic configuration files to work with Docker. Send an [e-mail to me](mailto:yaodong.zhao@utah.edu) if you have any question.

## How to Setup Development Environment

### Start Front-end Development Server

Before start, please apply a API token from [FileStack](https://www.filestack.com).
Put the API token into file `frontend/app/templates/components/files-picker.hbs`.

Then, start a container with Node installed.
```
cd frontend/
docker run --rm -it -p 3000:3000 -v "$(pwd)":/srv node:6.14.1 /bin/bash
```

Then, in the shell of the container, install dependencies if it's the first run:

```
cd /srv
npm install ember-cli
npm install
```

It takes a while before you can start the Ember server:

```
ember serve
```

### Start Backend Development Server

Build the image on the first time you run the server.

```
cd backend/
docker build . -t vis-extension-backend
```

Then when you need start a backend server, just run:

```
docker run --rm -it -p 8000:8000 -v "$(pwd)":/srv vis-extension-backend /bin/bash
```

In the shell of the container, start the server with

```
cd /srv/
python manage.py migrate
python manage.py runserver
```

## Deployment

Since we run this project in our internal server. I use Docker Compose to deploy it.

```
docker-compose build
docker-compose up -d
```
