#!/bin/bash
 
NAME="wheat-api"                                  # Name of the application
DJANGODIR=/workspace/wheat-api/wheat            # Django project directory
PORT=8484
USER=develop                                       # the user to run as
GROUP=develop # the group to run as
NUM_WORKERS=4                                     # how many worker processes should Gunicorn spawn
TIME_OUT=90
DJANGO_SETTINGS_MODULE=settings             # which settings file should Django use
DJANGO_WSGI_MODULE=wsgi                     # WSGI module name
GUNICORN_ACCESS_LOG=/workspace/wheat-api/wheat/logs/gunicorn-access.log
GUNICORN_ERROR_LOG=/workspace/wheat-api/wheat/logs/gunicorn-error.log
 
echo "Starting $NAME as `whoami`"
 
# Activate the virtual environment
cd $DJANGODIR
source /workspace/Envs/wheat-api/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$PYTHONPATH:$DJANGODIR
echo $PYTHONPATH 
# Create the run directory if it doesn't exist
# RUNDIR=$(dirname $SOCKFILE)
# test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --timeout $TIME_OUT \
  --user=$USER --group=$GROUP \
  --bind=:$PORT \
  --access-logfile=$GUNICORN_ACCESS_LOG \
  --error-logfile=$GUNICORN_ERROR_LOG \
  --log-level=error \
