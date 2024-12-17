# JKUClassNotifier

## Intro
Telegram community in Johannes Kepler University is pretty big but there is nothing software oriented in this media created. I know that a lot of people would prefer get notifications about their classes in their mostly used app, so that's why I created it. At 12 am it notifies students about today's classes.

## Deployment 
Digital Ocean Droplet - postgreSQL and telegram bot as docker images.
Check it out in telegram - @JKUClassNotifierBOT

## Installation and Setup 
```bash
git clone git@github.com:nikitazuevblago/JKUClassNotifier.git
cd JKUClassNotifier
pip install -r requirements.txt
python bot.py
```
* Don't forget to create .env file with necessary variables

## Technologies Used
* aiogram
* psycopg2
* ics

## File structure
bot.py - bot structure
db_interaction.py - interaction with database
custom_logging.py - configured logger
schedule.py - generator of post with today's classes