import os
import requests
import openai

def get_fmp_quote(symbol):
    API_KEY = os.environ['FMP_KEY']
    url = f'https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={API_KEY}'
    response = requests.get(url)
    print(f"Запрос к FMP: {url}")
    print(f"Ответ: {response.text}")
    data = response.json()
    try:
        price = float(data[0]['price'])
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

def gpt_analysis(xauusd, eurusd, gbpusd, news):
    openai.api_key = os.environ['OPENAI_API_KEY']
    prompt = f"""Ты — финансовый аналитик. Вот свежие данные:
Золото (XAU/USD): {xauusd:.2f}
EUR/USD: {eurusd:.4f}
GBP/USD: {gbpusd:.4f}
Новости: {news}

Сделай краткий прогноз на сегодня для валют и золота, выдели возможные риски и драйверы. Пиши лаконично, 2-4 предложения.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # или "gpt-4", если есть доступ
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def make_report():
    xauusd = get_fmp_quote('GCUSD')
    eurusd = get_fmp_quote('EURUSD')
    gbpusd = get_fmp_quote('GBPUSD')

    if None in [xauusd, eurusd, gbpusd]:
        return "Не удалось получить данные по золоту или валютам. Подробности смотри в логах GitHub Actions."

    news = get_news()
    try:
        forecast = gpt_analysis(xauusd, eurusd, gbpusd, news)
    except Exception as e:
        forecast = f"Не удалось получить прогноз от GPT: {e}"

    return f"""🌅 Доброе утро! Финансовый обзор:

🥇 XAU/USD: {xauusd:.2f}
💶 EUR/USD: {eurusd:.4f}
💷 GBP/USD: {gbpusd:.4f}

📰 Важные новости:
{news}

🤖 Прогноз и анализ от GPT:
{forecast}

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
