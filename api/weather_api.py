import requests
from datetime import datetime
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_KEY = "a5765ebb593f55db1f0d896faff51969"


def get_current_weather(city):
    if not city or not city.strip():
        return {"error": "Введите название города"}, 400
    
    urls = [
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru",
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru",
    ]
    
    for url in urls:
        try:
            print(f"Пытаемся получить погоду: {url}")
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if response.status_code == 200:
                result = {
                    "success": True,
                    "city": data['name'],
                    "country": data.get('sys', {}).get('country', ''),
                    "temp": round(data['main']['temp'], 1),
                    "feels_like": round(data['main']['feels_like'], 1),
                    "humidity": data['main']['humidity'],
                    "wind": data['wind']['speed'],
                    "description": data['weather'][0]['description'].capitalize(),
                    "icon": data['weather'][0]['icon']
                }
                return result, 200
            elif response.status_code == 404:
                return {"error": f"Город '{city}' не найден"}, 404
        except requests.exceptions.Timeout:
            print(f"Таймаут для URL: {url}")
            continue
        except Exception as e:
            print(f"Ошибка для URL {url}: {e}")
            continue
    
    return {"error": "Сервер погоды не отвечает. Попробуйте позже."}, 504


def get_forecast(city):
    if not city or not city.strip():
        return {"error": "Введите название города"}, 400

    urls = [
        f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru",
        f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru",
    ]
    
    for url in urls:
        try:
            print(f"Пытаемся получить прогноз: {url}")
            response = requests.get(url, timeout=20)  
            data = response.json()
            
            if response.status_code == 200:
                days = []
                seen_dates = set()
                
                for item in data['list']:
                    date = item['dt_txt'].split()[0]
                    if date not in seen_dates and len(days) < 5:
                        seen_dates.add(date)
                        days.append({
                            "date": date,
                            "temp": round(item['main']['temp'], 1),
                            "temp_min": round(item['main']['temp_min'], 1),
                            "temp_max": round(item['main']['temp_max'], 1),
                            "description": item['weather'][0]['description'].capitalize(),
                            "icon": item['weather'][0]['icon']
                        })
                
                result = {
                    "success": True,
                    "city": data['city']['name'],
                    "country": data['city'].get('country', ''),
                    "days": days
                }
                return result, 200
            elif response.status_code == 404:
                return {"error": f"Город '{city}' не найден"}, 404
        except requests.exceptions.Timeout:
            print(f"Таймаут для URL прогноза: {url}")
            continue
        except Exception as e:
            print(f"Ошибка для URL прогноза {url}: {e}")
            continue
    
    return {"error": "Сервер прогноза не отвечает. Попробуйте позже."}, 504


