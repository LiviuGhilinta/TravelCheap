import requests
import datetime
import os
from dotenv import load_dotenv

def convert(date_time):
    format = '%Y-%m-%d'
    datetime_str = datetime.datetime.strptime(date_time,format)
    return datetime_str
def Find_the_weather(city,date1,date2):
    def fahrenheit_to_celsius(f):
        return int((f - 32) * 5 / 9)
    if date2 is None:
        date2 = (convert(date1) + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
    load_dotenv()
    api_key = os.getenv("WeatherApi")

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{date1}/{date2}?key={api_key}"

    response = requests.get(url)
    vreme_zile = list()

    if response.status_code == 200:
        data = response.json()
        
        for day in data['days']:
            date = day['datetime']
            avgtemp = fahrenheit_to_celsius(day['temp'] )
            maxtemp = fahrenheit_to_celsius(day['tempmax']  ) 
            desc = day['conditions']
            vreme_zile.append({
                    "data": day['datetime'],
                    "medie": fahrenheit_to_celsius(day['temp']),
                    "maxima": fahrenheit_to_celsius(day['tempmax']),
                    'desc' : desc
                })
        
            print(f"Data : {date} \n Medie temperatura per zi: {avgtemp}°C,\n Maxima zilei:{maxtemp} \n {desc}")
    else:
        print("Eroare:", response.status_code)
    return vreme_zile