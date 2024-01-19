import requests
import time

API_KEY = "9trdAcA24NDtaBdbjO4LACmE36SY1TQwdlIkmRvB"
SECRET_KEY = "7mkO98HE3Dc97Jemedn4YjKhIi5sJTsDcO8HtxWy"
BASE_URL = "https://api.upbit.com"

def get_coin_data():
    url = f"{BASE_URL}/v1/market/all"
    response = requests.get(url)
    data = response.json()
    return data

def calculate_percentage_change(open_price, close_price):
    percentage_change = ((close_price - open_price) / open_price) * 100
    return percentage_change

def get_top_gainers(days, data):
    top_gainers = []
    for coin in data:
        market = coin['market']
        url = f"{BASE_URL}/v1/candles/days?market={market}&count={days}"
        response = requests.get(url)
        candles = response.json()
        if len(candles) >= days:
            open_price = candles[-days]['opening_price']
            close_price = candles[-1]['trade_price']
            percentage_change = calculate_percentage_change(open_price, close_price)
            top_gainers.append((coin['market'], coin['korean_name'], percentage_change))
    top_gainers.sort(key=lambda x: x[2], reverse=True)
    return top_gainers

def buy_coin(market, price, quantity):
    query = {
        "market": market,
        "side": "bid",
        "price": str(price),
        "ord_type": "price",
    }
    url = f"{BASE_URL}/v1/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    response = requests.post(url, headers=headers, json=query)
    result = response.json()
    print(f"매수 주문 결과: {result}")

def sell_coin(market, price, quantity):
    query = {
        "market": market,
        "side": "ask",
        "volume": str(quantity),
        "ord_type": "market",
    }
    url = f"{BASE_URL}/v1/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    response = requests.post(url, headers=headers, json=query)
    result = response.json()
    print(f"매도 주문 결과: {result}")

def main():
    days = 7  # 최근 7일간의 상승률을 계산합니다.
    coin_data = get_coin_data()
    top_gainers = get_top_gainers(days, coin_data)
    
    print(f"{days}일간의 상승률이 높은 코인들:")
    for coin in top_gainers:
        market, name, percentage_change = coin
        print(f"코인명: {name}, 마켓: {market}, 상승률: {percentage_change:.2f}%")
        
        # 상승률이 높은 코인을 자동으로 매매하도록 설정합니다.
        if percentage_change > 0:
            # 적절한 매매 전략을 구현하고, 매수 또는 매도 주문을 실행합니다.
            # 여기에 매매 전략과 주문 실행 코드를 작성해주세요.
            # 예시: buy_coin(market, price, quantity)
            # 예시: sell_coin(market, price, quantity)
            pass
        
        time.sleep(1)  # API 요청 제한을 준수하기 위해 1초 딜레이를 추가합니다.

if __name__ == "__main__":
    main()
