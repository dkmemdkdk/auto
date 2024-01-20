import logging
import time
import pyupbit

# 인증 정보
API_KEY = "9trdAcA24NDtaBdbjO4LACmE36SY1TQwdlIkmRvB"
SECRET_KEY = "7mkO98HE3Dc97Jemedn4YjKhIi5sJTsDcO8HtxWy"
upbit = pyupbit.Upbit(API_KEY, SECRET_KEY)

# 최근 일주일 동안 상승률이 높은 상위 5개 코인 조회
def get_top_coins():
    tickers = pyupbit.get_tickers(fiat="KRW")
    coin_prices = []
    for ticker in tickers:
        try:
            df = pyupbit.get_ohlcv(ticker, interval="day", count=8)
            if df is not None and len(df) == 8:
                week_ago_close = df['close'].iloc[0]
                current_close = df['close'].iloc[-1]
                price_change_rate = (current_close - week_ago_close) / week_ago_close * 100
                coin_prices.append((ticker, price_change_rate))
        except Exception as e:
            logging.error(f"티커 조회 중 오류 발생: {ticker}: {e}")
            continue

    top_coins = sorted(coin_prices, key=lambda x: x[1], reverse=True)[:5]
    return [coin[0] for coin in top_coins]

# 변동성 돌파 전략
def volatility_breakthrough_strategy(coin):
    try:
        df = pyupbit.get_ohlcv(coin, interval="day", count=2)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.5
        current_price = pyupbit.get_current_price(coin)
        if current_price >= target_price:
            krw_balance = upbit.get_balance("KRW")
            if krw_balance is not None and 5000 <= krw_balance <= 6000:  # 잔액이 5000원 이상, 6000원 이하일 때만 주문
                upbit.buy_market_order(coin, krw_balance/5)
    except Exception as e:
        logging.error(f"변동성 돌파 전략 중 오류 발생: {coin}: {e}")

# 거래량 매매 전략
def volume_trading_strategy(coin):
    try:
        df = pyupbit.get_ohlcv(coin, interval="day", count=2)
        if df.iloc[1]['volume'] > df.iloc[0]['volume']:
            krw_balance = upbit.get_balance("KRW")
            if krw_balance is not None and 5000 <= krw_balance <= 6000:  # 잔액이 5000원 이상, 6000원 이하일 때만 주문
                upbit.buy_market_order(coin, krw_balance/5)
    except Exception as e:
        logging.error(f"거래량 매매 전략 중 오류 발생: {coin}: {e}")

# 매도 전략
def sell_if_profit(coin):
    try:
        avg_buy_price = upbit.get_avg_buy_price(coin)
        current_price = pyupbit.get_current_price(coin)

        if current_price and avg_buy_price and ((current_price - avg_buy_price) / avg_buy_price) >= 0.005:  # 0.5% 이상 수익이 발생한 경우
            coin_balance = upbit.get_balance(coin)
            upbit.sell_market_order(coin, coin_balance)
    except Exception as e:
        logging.error(f"매도 전략 중 오류 발생: {coin}: {e}")

while True:
    try:
        # 최근 일주일 동안 상승률이 높은 상위 5개 코인 조회
        coins = get_top_coins()

        # 매매 전략 실행
        for coin in coins:
            try:
                volatility_breakthrough_strategy(coin)  # 매수 전략
                volume_trading_strategy(coin)  # 매수 전략
                sell_if_profit(coin)  # 매도 전략
            except Exception as e:
                logging.error(f"매매 전략 중 오류 발생: {coin}: {e}")
                continue

        time.sleep(1)
    except Exception as e:
        logging.error(f"전체 프로세스 중 오류 발생: {e}")


