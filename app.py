from flask import Flask, render_template, request, jsonify, make_response
import requests
from bs4 import BeautifulSoup
import uuid
import os
from datetime import datetime
import random

app = Flask(__name__)

# API ключ OpenWeatherMap
API_KEY = "a5765ebb593f55db1f0d896faff51969"

def log_action(user_id, action, details=""):
    """Логирование действий пользователя"""
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/{user_id}.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}: {details}\n")

@app.route('/')
def index():
    """Главная страница"""
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())[:8]
    
    response = make_response(render_template('index.html', user_id=user_id))
    response.set_cookie('user_id', user_id, max_age=60*60*24*365)
    return response

@app.route('/api/weather/current')
def current_weather():
    """API: Текущая погода"""
    city = request.args.get('city', '').strip()
    user_id = request.args.get('user_id', 'unknown')
    
    if not city:
        return jsonify({"error": "Введите название города"}), 400
    
    try:
        url = f"http://ru.api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=10)
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
            log_action(user_id, "current_weather", f"Город: {city}")
            return jsonify(result)
        else:
            return jsonify({"error": f"Город '{city}' не найден"}), 404
    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500

@app.route('/api/weather/forecast')
def forecast_weather():
    """API: Прогноз на 5 дней"""
    city = request.args.get('city', '').strip()
    user_id = request.args.get('user_id', 'unknown')
    
    if not city:
        return jsonify({"error": "Введите название города"}), 400
    
    try:
        url = f"http://ru.api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=10)
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
            log_action(user_id, "forecast_5days", f"Город: {city}")
            return jsonify(result)
        else:
            return jsonify({"error": f"Город '{city}' не найден"}), 404
    except Exception as e:
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500

@app.route('/api/quote')
def get_quote():
    """API: Цитата о погоде (скрапинг + бэкап)"""
    user_id = request.args.get('user_id', 'unknown')
    
    quotes_backup = [
        {"text": "Нет плохой погоды, есть плохая одежда.", "author": "Народная мудрость"},
        {"text": "Погода — это то, о чем мы все говорим, но ничего не можем с этим поделать.", "author": "Марк Твен"},
        {"text": "Климат — это то, чего мы ожидаем, а погода — то, что получаем.", "author": "Роберт Хайнлайн"},
        {"text": "После дождя всегда приходит солнце.", "author": "Китайская пословица"},
        {"text": "Погода делает нас ближе к природе.", "author": "Аноним"},
        {"text": "Лучшее украшение погоды — хорошее настроение.", "author": "Народная мудрость"},
    ]
    
    try:
        url = "https://www.aphorism.ru/comments/weather/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        quote_elem = soup.find('div', class_='description')
        if quote_elem:
            quote_text = quote_elem.get_text().strip()
            log_action(user_id, "scraping_quote", "Успешно с сайта aphorism.ru")
            return jsonify({
                "success": True,
                "text": quote_text,
                "author": "aphorism.ru",
                "scraped": True
            })
    except:
        pass
    
    quote = random.choice(quotes_backup)
    log_action(user_id, "scraping_quote", "Использована локальная база цитат")
    return jsonify({
        "success": True,
        "text": quote["text"],
        "author": quote["author"],
        "scraped": False
    })

@app.route('/api/logs')
def get_logs():
    """API: Получить логи пользователя"""
    user_id = request.args.get('user_id', 'unknown')
    log_file = f"logs/{user_id}.log"
    
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            logs = [line.strip() for line in lines[-50:]]
        return jsonify({"success": True, "logs": logs})
    else:
        return jsonify({"success": True, "logs": ["Нет записей в логе"]})

if __name__ == '__main__':
    print("=" * 50)
    print("🌤️ AURA WEATHER ПРИЛОЖЕНИЕ ЗАПУЩЕНО")
    print("=" * 50)
    print("📍 Откройте в браузере: http://127.0.0.1:5000")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)