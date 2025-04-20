import os
import requests
import time

def get_index(symbol, market=None):
    API_KEY = os.environ['ALPHA_VANTAGE_KEY']
    if market:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}.{market}&apikey={API_KEY}'
    else:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    try:
        price = float(data['Global Quote']['05. price'])
        return price
    except Exception:
        return None

def get_fx(from_symbol, to_symbol):
    API_KEY = os.environ['ALPHA_VANTAGE_KEY']
    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_symbol}&to_currency={to_symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    try:
        rate = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        return rate
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

def analyze_impact(sp500, eurusd):
    impact = ""
    if sp500 and sp500 > 5000:
        impact += "Рост S&P 500 может поддержать позитивное открытие GER40.\n"
    if eurusd and eurusd < 1.08:
        impact += "Слабый евро может поддержать экспортеров GER40.\n"
    if not impact:
        impact = "Существенных внешних драйверов для GER40 не отмечается."
    return impact

def make_report():
    # Индексы и валюты
    ger40 = get_index('GDAXI', 'F')      # DAX (GER40)
    time.sleep(12)
    sp500 = get_index('^GSPC')           # S&P 500
    time.sleep(12)
    eu50 = get_index('SX5E', 'F')        # Euro Stoxx 50 (EU50)
    time.sleep(12)
    fdax = get_index('FDAX', 'F')        # Фьючерс на DAX (может не поддерживаться, зависит от Alpha Vantage)
    time.sleep(12)
    xauusd = get_fx('XAU', 'USD')        # Золото к доллару
    time.sleep(12)
    eurusd = get_fx('EUR', 'USD')        # EUR/USD
    time.sleep(12)
    gbpusd = get_fx('GBP', 'USD')        # GBP/USD

    # Проверка данных
    if None in [ger40, sp500, eu50, fdax, xauusd, eurusd, gbpusd]:
        return "Не удалось получить данные по индексам или валютам. Попробуйте позже."

    news = get_news()
    impact = analyze_impact(sp500, eurusd)
    return f"""🌅 Доброе утро! Финансовый обзор:

🇩🇪 GER40 (DAX): {ger40:.2f}
🇪🇺 Euro Stoxx 50 (EU50): {eu50:.2f}
🇩🇪 FDAX (фьючерс на DAX): {fdax:.2f}
🇺🇸 S&P 500: {sp500:.2f}
💶 EUR/USD: {eurusd:.4f}
💷 GBP/USD: {gbpusd:.4f}
🥇 XAU/USD: {xauusd:.2f}

📰 Важные новости:
{news}

📊 Возможное влияние на GER40:
{impact}

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
