from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from suntime import Sun, SunTimeException
import pytz

load_dotenv()

def IsSunUp():

    sun = Sun(float(os.getenv('LATITUDE')), float(os.getenv('LONGITUDE')))

    today_dawn = sun.get_sunrise_time() + timedelta(minutes=-15)
    today_twilight = sun.get_sunset_time() + timedelta(minutes = 15)

    now = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))

    if os.getenv('DEBUG', False) == "True":
        print('The sun is up:', now > today_dawn and now < today_twilight, '\nTime now:', now, '\nToday Dawn:', today_dawn, '\nToday Twilight:', today_twilight)

    return (now > today_dawn and now < today_twilight)
