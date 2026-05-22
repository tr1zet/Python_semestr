import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

quote_cache = {
    "data": None,
    "timestamp": None,
    "last_quote": None
}


def get_quote():
    if quote_cache["data"] and quote_cache["timestamp"]:
        time_diff = datetime.now() - quote_cache["timestamp"]
        if time_diff < timedelta(hours=1):
            return quote_cache["data"]
    
    #CКРАПИНГ 
    try:
        url = "https://www.aphorism.ru/comments/weather/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            quote_elem = None
            selectors = [
                ('div', 'description'),
                ('div', 'quote-text'),
                ('div', 'content'),
                ('div', 'text'),
                ('p', None)
            ]
            
            for tag, class_name in selectors:
                if class_name:
                    quote_elem = soup.find(tag, class_=class_name)
                else:
                    quote_elem = soup.find(tag)
                if quote_elem:
                    break
            
            if quote_elem:
                quote_text = quote_elem.get_text().strip()
                quote_text = quote_text.split('\n')[0].strip()
                
                if 20 < len(quote_text) < 500:
                    result = {
                        "success": True,
                        "text": quote_text,
                        "author": "aphorism.ru",
                        "source": "scraping",
                        "scraped": True
                    }
                    quote_cache["data"] = result
                    quote_cache["timestamp"] = datetime.now()
                    return result
    except Exception as e:
        print(f"Ошибка скрапинга: {e}")
    
    #API ЦИТАТ
    try:
        api_url = "https://api.quotable.io/random"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            quote_text = data.get('content', '')
            quote_author = data.get('author', 'Unknown')
            
            if quote_text and len(quote_text) < 500:
                result = {
                    "success": True,
                    "text": quote_text,
                    "author": quote_author,
                    "source": "Quotable.io API",
                    "scraped": False
                }
                quote_cache["data"] = result
                quote_cache["timestamp"] = datetime.now()
                return result
    except Exception as e:
        print(f"Ошибка API: {e}")
    
    #УРОВЕНЬ 3: ЛОКАЛЬНЫЙ БЭКАП
    ultimate_backup = [
        {"text": "Нет плохой погоды, есть плохая одежда.", "author": "Народная мудрость"},
        {"text": "После дождя всегда приходит солнце.", "author": "Китайская пословица"},
        {"text": "Климат — это то, чего мы ожидаем, а погода — то, что получаем.", "author": "Роберт Хайнлайн"},
        {"text": "Погода — это то, о чем мы все говорим, но ничего не можем с этим поделать.", "author": "Марк Твен"},
        {"text": "Лучшее украшение погоды — хорошее настроение.", "author": "Народная мудрость"},
        {"text": "Солнце светит даже в самую темную тучу.", "author": "Аноним"},
        {"text": "Погода делает нас ближе к природе.", "author": "Аноним"},
        {"text": "У природы нет плохой погоды — каждая погода благодать.", "author": "Эльдар Рязанов"},
        {"text": "Солнце заходит, чтобы снова взойти.", "author": "Латинская пословица"},
        {"text": "Ветер перемен всегда дует в правильном направлении.", "author": "Древняя мудрость"},
        {"text": "Каждая погода имеет свою красоту.", "author": "Японская пословица"},
        {"text": "Тот, кто не знает погоды, не должен выходить в море.", "author": "Арабская пословица"}
    ]
    
    available_quotes = [q for q in ultimate_backup if q["text"] != quote_cache.get("last_quote")]
    if not available_quotes:
        available_quotes = ultimate_backup
    
    selected_quote = random.choice(available_quotes)
    
    result = {
        "success": True,
        "text": selected_quote["text"],
        "author": selected_quote["author"],
        "source": "backup",
        "scraped": False,
        "backup": True
    }
    
    quote_cache["data"] = result
    quote_cache["timestamp"] = datetime.now()
    quote_cache["last_quote"] = selected_quote["text"]
    
    return result


def refresh_quote_cache():
    global quote_cache
    quote_cache = {
        "data": None,
        "timestamp": None,
        "last_quote": quote_cache.get("last_quote")
    }
    return {"success": True, "message": "Кэш цитат очищен"}