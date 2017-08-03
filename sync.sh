#!/usr/bin/env bash
rsync -azP . pi@192.168.0.133:~/App/BlueMarine/ --exclude=node_modules/
