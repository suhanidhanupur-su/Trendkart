#!/bin/bash
pip install -r requirements.txt
python E_commerce/manage.py collectstatic --noinput --clear
