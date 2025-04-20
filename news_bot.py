import os
import yfinance as yf
import requests

def get_indices_and_fx():
    # Получаем данные по индексам и валютам
    ger40 = yf.Ticker("^GDAXI")  # GER40 (DAX)
    sp500 = yf.Ticker("^GSPC")   # S&P 500
    eurusd = yf.Ticker("EURUSD=X")
    usdeur = yf.Ticker("USDEUR=X")

    ger40_data = ger40.history(period="1d")
    sp500_data = sp500.history(period="1d")
    eurusd_data = eurusd.history(period="1d")

    ger40_close = ger40_data['Close'].iloc[-1]
    sp500_close = sp500_data['Close'].iloc[-1]
    eurusd_close = eurusd_data['Close'].iloc[-1]

    return ger40_close, sp500_close, eurusd_close

def get_news():
    # Пример с NewsAPI (нужен бесплатный ключ)
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
    # Примитивный анализ влияния на GER40
    impact = ""
    if sp500 > 5000:
        impact += "Рост S&P 500 может поддержать позитивное открытие GER40.\n"
    if eurusd < 1.08:
        impact += "Слабый евро может поддержать экспортеров GER40.\n"
    if not impact:
        impact = "Существенных внешних драйверов для GER40 не отмечается."
    return impact

def make_report():
    ger40, sp500, eurusd = get_indices_and_fx()
    news = get_news()
    impact = analyze_impact(sp500, eurusd)
    return f"""🌅 Доброе утро! Финансовый обзор:

🇩🇪 GER40 (DAX): {ger40:.2f}
🇺🇸 S&P 500: {sp500:.2f}
💶 EUR/USD: {eurusd:.4f}

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
    requests.post(url, data=payload)

def main():
    try:
        report = make_report()
        send_telegram_message(report)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()