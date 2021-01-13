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
  docker run -p 8990:8990 -v /docker_yqueuer/yqueuer:/yqueuer --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL yqueuer

Run Import
  docker run -v /docker_yqueuer/yqueuer:/yqueuer --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL yqueuer python manage.py import

Run Python Shell with Django #django_shell
  winpty docker run -i -t -v /docker_yqueuer/yqueuer:/yqueuer --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL yqueuer python manage.py shell

Run bash in container
  winpty docker run -i -t -v /docker_yqueuer/yqueuer:/yqueuer  --env SECRET_KEY --env DB_USER --env DB_PASS --env ALLOWED_HOSTS --env YOUTUBE_API_KEY --env DATABASE_URL --env MAILGUN_API_KEY --env MAILGUN_DOMAIN --env PROJECT_EMAIL  yqueuer /bin/bash


## Deploy
  heroku login
  cat $HOME/_netrc
  git push heroku master
    username (from cat $HOME/_netrc)
    password (from cat $HOME/_netrc)

## Debug DB
Run Python Shell with Django (search #django_shell)

```python
# Import Useful
from frontend.models import Channel, Video, RUserVideo, RUserChannel
from django.contrib.auth.models import User
from django.db.models import Max, Min, Avg, Count
import pprint

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


## Docker
- Build
  docker image rm yqueuer
  docker build -f docker/Dockerfile --rm -t yqueuer yqueuer

- Test docker
  docker image ls
