import os
import requests

def get_finnhub_fx(symbol):
    API_KEY = os.environ['FINNHUB_KEY']
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}'
    response = requests.get(url)
    print(f"Запрос к Finnhub: {url}")
    print(f"Ответ: {response.text}")
    data = response.json()
    try:
        price = float(data['c'])
        return price
    except Exception:
        return None

def get_news():
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    if not NEWS_API_KEY:
        return "Новости не получены (нет API ключа)."
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=ru&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    articles = data.get("articles", [])[:3]
    news_list = []
    for art in articles:
        news_list.append(f"• {art['title']}")
    return "\n".join(news_list) if news_list else "Нет свежих новостей."

def make_report():
    eurusd = get_finnhub_fx('OANDA:EUR_USD')
    gbpusd = get_finnhub_fx('OANDA:GBP_USD')
    if eurusd is None or gbpusd is None:
        return "Не удалось получить данные по валютам. Подробности смотри в логах GitHub Actions."
    news = get_news()
    return f"""🌅 Доброе утро! Финансовый обзор:

💶 EUR/USD: {eurusd:.4f}
💷 GBP/USD: {gbpusd:.4f}

📰 Важные новости:
{news}

Хорошего дня и удачных инвестиций!
"""

def send_telegram_message(message):
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    print(response.text)
    return response.json()

def main():
    try:
        report = make_report()
        send_telegram_message(report)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
