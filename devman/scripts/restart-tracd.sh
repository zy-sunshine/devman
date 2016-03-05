#!/bin/bash

ps aux | grep "/home/devman/trac" | awk '{print $2}' | xargs kill -9
tracd -d -b 127.0.0.1 -p 3050 --pidfile=/home/devman/tracd.3050 --protocol=http -e /home/devman/trac --base-path=/dmprojs/trac
