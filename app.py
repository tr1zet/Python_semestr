from flask import Flask, render_template, request, jsonify, make_response
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем  модули API
from api.weather_api import get_current_weather, get_forecast
from api.quote_api import get_quote, refresh_quote_cache
from api.logs_api import log_action, get_user_logs, clear_user_logs

app = Flask(__name__)


@app.route('/')
def index():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())[:8]
    
    response = make_response(render_template('index.html', user_id=user_id))
    response.set_cookie('user_id', user_id, max_age=60*60*24*365)
    return response


@app.route('/api/weather/current')
def current_weather_endpoint():
    city = request.args.get('city', '').strip()
    user_id = request.args.get('user_id', 'unknown')
    
    result, status_code = get_current_weather(city)
    
    if status_code == 200:
        log_action(user_id, "current_weather", f"Город: {city}")
    else:
        log_action(user_id, "current_weather_error", f"Город: {city}, Ошибка: {result.get('error', 'Unknown')}")
    
    return jsonify(result), status_code


@app.route('/api/weather/forecast')
def forecast_endpoint():
    city = request.args.get('city', '').strip()
    user_id = request.args.get('user_id', 'unknown')
    
    result, status_code = get_forecast(city)
    
    if status_code == 200:
        log_action(user_id, "forecast_5days", f"Город: {city}")
    else:
        log_action(user_id, "forecast_error", f"Город: {city}, Ошибка: {result.get('error', 'Unknown')}")
    
    return jsonify(result), status_code


@app.route('/api/quote')
def quote_endpoint():
    user_id = request.args.get('user_id', 'unknown')
    
    result = get_quote()
    
    if result.get('success'):
        log_action(user_id, "get_quote", f"Источник: {result.get('source', 'unknown')}")
    else:
        log_action(user_id, "get_quote_error", "Не удалось получить цитату")
    
    return jsonify(result)


@app.route('/api/quote/refresh')
def refresh_quote_endpoint():
    user_id = request.args.get('user_id', 'unknown')
    result = refresh_quote_cache()
    log_action(user_id, "refresh_quote_cache", "Кэш очищен")
    return jsonify(result)


@app.route('/api/logs')
def logs_endpoint():
    user_id = request.args.get('user_id', 'unknown')
    logs = get_user_logs(user_id)
    log_action(user_id, "view_logs", f"Просмотр истории ({len(logs)} записей)")
    return jsonify({"success": True, "logs": logs})


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs_endpoint():
    user_id = request.args.get('user_id', 'unknown')
    success = clear_user_logs(user_id)
    if success:
        log_action(user_id, "clear_logs", "История очищена")
        return jsonify({"success": True, "message": "История очищена"})
    else:
        return jsonify({"success": False, "message": "Файл логов не найден"}), 404


@app.route('/api/stats')
def stats_endpoint():
    user_id = request.args.get('user_id', 'unknown')
    
    logs = get_user_logs(user_id, limit=1000)
    
    stats = {
        "total_requests": len([l for l in logs if l != "Нет записей в логе"]),
        "weather_checks": len([l for l in logs if "current_weather" in l]),
        "forecast_checks": len([l for l in logs if "forecast" in l]),
        "quotes_received": len([l for l in logs if "get_quote" in l])
    }
    
    log_action(user_id, "view_stats", f"Статистика: {stats}")
    return jsonify({"success": True, "stats": stats})


if __name__ == '__main__':
    print("=" * 60)
    print("🌤️ AURA WEATHER ПРИЛОЖЕНИЕ ЗАПУЩЕНО")
    print("=" * 60)
    print("📍 Откройте в браузере: http://127.0.0.1:5000")
    print("")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)