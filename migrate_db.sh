#!/usr/bin/env bash

REPO_DIR=$(pwd)
cd src/
if [ ! -d migrations ]; then
  python3 -m flask db init
fi
python3 -m flask db migrate
python3 -m flask db upgrade

if [ "$1" == "--fake-data-population" ]; then
  cd $REPO_DIR
  python3 fake_data_generator.py
fi
exit 0