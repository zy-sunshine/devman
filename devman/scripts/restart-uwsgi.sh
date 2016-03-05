#!/bin/bash

ps aux | grep "uwsgi-devman" | awk '{print $2}' | xargs kill -9
/home/devman/uwsgi-venv/bin/uwsgi --ini /home/devman/works/devman/devman/scripts/uwsgi-devman.ini
