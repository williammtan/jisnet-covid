#!/bin/bash

# export chromedriver path (assuming that you have installed chromedriver)
export PATH=$PATH:/usr/local/bin/

pip install -r requirements.txt
nohup python main.py --update-time 60 --headless --credentials password.json > /dev/null 2>&1 &