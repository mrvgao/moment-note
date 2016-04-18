#!/bin/bash
 
# default configuration
NAME="wheat-api"                                  # Name of the application
DJANGODIR=/workspace/wheat-api/wheat            # Django project directory
PORT=8484
USER=develop                                       # the user to run as
GROUP=develop # the group to run as
NUM_WORKERS=4                                     # how many worker processes should Gunicorn spawn
TIME_OUT=90
DJANGO_WSGI_MODULE=wsgi                     # WSGI module name


###### Get command line options ###### 
OPTIND=1         # Reset in case getopts has been used previously in the shell.
while getopts "h?n:d:p:u:g:c:w:t:" opt; do
    case "$opt" in
    h|\?)
        echo "help..."
        exit 0
        ;;
    n)  NAME=$OPTARG
        ;;
    d)  DJANGODIR=$OPTARG
        ;;
    p)  PORT=$OPTARG
        ;;
    u)  USER=$OPTARG
        ;;
    g)  GROUP=$OPTARG
        ;;
    c)  NUM_WORKERS=$OPTARG
        ;;
    w)  DJANGO_WSGI_MODULE=$OPTARG
        ;;
    t)  TIME_OUT=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

echo "Configurations..."
echo
echo "NAME=$NAME"
echo "DJANGODIR=$DJANGODIR"
echo "PORT=$PORT"
echo "USER=$USER"
echo "GROUP=$GROUP"
echo "NUM_WORKERS=$NUM_WORKERS"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "TIME_OUT=$TIME_OUT" 
echo 

###### End Get command line options ###### 


DJANGO_SETTINGS_MODULE=settings             # which settings file should Django use
GUNICORN_ACCESS_LOG=$DJANGODIR/logs/gunicorn-access.log
GUNICORN_ERROR_LOG=$DJANGODIR/logs/gunicorn-error.log
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
  --worker-class eventlet
