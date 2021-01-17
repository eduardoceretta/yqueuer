# Yqueuer Docker Version

## Requirements
- Virtual Env
- Docker
- Heroku tools

## Init Development
Setup
    ./init_docker_machine.sh
  OR just run manually
    docker-machine.exe restart box
    eval $("docker-machine" env box)
    source config/export_env

Run Server
  docker run -p 8990:8990 -v /docker_yqueuer/yqueuer:/yqueuer --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS=localhost --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL yqueuer

Run Import
  docker run -v /docker_yqueuer/yqueuer:/yqueuer --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL yqueuer python manage.py import

Run Python Shell with Django #django_shell
  winpty docker run -i -t -v /docker_yqueuer/yqueuer:/yqueuer --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL yqueuer python manage.py shell

Run bash in container
  winpty docker run -i -t -v /docker_yqueuer/yqueuer:/yqueuer  --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL  yqueuer /bin/bash

SSH into Heroku Dyno
  heroku ps:exec -a yqueuer


## Deploy
  heroku login
  cat $HOME/_netrc
  git push heroku master
    username (from cat $HOME/_netrc)
    password (from cat $HOME/_netrc)

Yqueuer2
  git push heroku-20 master

## DB
Run Python Shell with Django (search #django_shell)

```python
# Import Useful
from frontend.models import Channel, Video, RUserVideo, RUserChannel
from django.contrib.auth.models import User
from django.db.models import Max, Min, Avg, Count
import pprint
from frontend.yqueuer_api import *

# select count(1) from table
Video.objects.all().count()

#describe table
pprint.pprint([str(x) for x in Channel._meta._get_fields()])

#select from table
Video.objects.filter(y_video_id = 'tqpRTuwpJVo')

# group by channel count videos
pprint.pprint([(x.title, x.num_videos) for x in Channel.objects.annotate(num_videos=Count('video'))])

#Show users and last login
pprint.pprint([(x.username, x.last_login.strftime("%Y-%m-%d %H:%M:%S") if x.last_login is not None else "NONE") for x in User.objects.all()])

#Show channels and name
pprint.pprint([(x.y_channel_id, x.name) for x in Channel.objects.all()])


# truncate table
Video.objects.all().delete()
```

parse from DATABASE_URL
  postgresql://[user[:password]@][hostname][:port][/dbname]

Connect to Database from docker
  docker run -it --rm  postgres psql -h <HOSTNAME> -U <USERNAME> -p <PORT> -d <DBNAME>

Dump database from docker
  docker run -it --rm  postgres pg_dump -h <HOSTNAME> -U <USERNAME> -p <PORT> -d <DBNAME> > dump.bak
  * This command will stop and wait for password but not ouput anything, just paste the password and wait

## Docker
- Build
  docker image rm yqueuer
  docker build -f docker/Dockerfile --rm -t yqueuer yqueuer
  docker build -f docker/Dockerfile27 --rm -t yqueuer27 yqueuer

- Test docker
  docker image ls

## Migrate Heroku App
Create Heroku APP
  heroku create --remote heroku-20 --stack heroku-20 yqueuer2
  app url: https://yqueuer2.herokuapp.com

Migrate Addons
  scheduler
    create
      heroku addons:create --remote heroku-20 scheduler
    see rules of old one
      heroku addons:open scheduler  -r heroku
    config new one
      heroku addons:open scheduler  -r heroku-20

Config Env
  Check old configs
    heroku config --shell --remote heroku
  Set new configs
    heroku config:set --remote heroku-20 key=value

Migrate Python]
  2to3 by sshing into python 3 image
  2to3 -w yqueuer/wsgi.py

Push
  heroku login
  cat $HOME/_netrc
  git push heroku-20 master
    username (from cat $HOME/_netrc)
    password (from cat $HOME/_netrc)