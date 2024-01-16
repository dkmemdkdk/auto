import pyupbit
import time
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # 원하는 로깅 레벨을 설정합니다.

def cal_target(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, "day")
        yesterday = df.iloc[-2]
        today = df.iloc[-1]
        yesterday_range = yesterday['high'] - yesterday['low']
        target = today['open'] + yesterday_range * 0.5
        return target
    except Exception as e:
        logging.error(f"Error in cal_target for {ticker}: {e}")
        return None

# API 키를 파일에서 로드합니다.
try:
    with open("upbit.txt") as f:
        lines = f.readlines()
        access = lines[0].strip()
        secret = lines[1].strip()
except FileNotFoundError:
    logging.error("upbit.txt 파일을 찾을 수 없습니다.")
    exit()

upbit = pyupbit.Upbit(access, secret)

# 변수 설정
coins = ["BTC", "ETH", "NEO", "MTL", "XRP", "ETC", "SNT", "WAVES", "XEM", "QTUM", "LSK", "STEEM", "XLM", "ARDR", "ARK", "STORJ", "GRS", "ADA", "SBD", "POWR"]
targets = {f"KRW-{coin}": cal_target(f"KRW-{coin}") for coin in coins}
op_modes = {f"KRW-{coin}": False for coin in coins}
holds = {f"KRW-{coin}": True if coin in ['BTC', 'ETH', 'LSK', 'ARK', 'POWR'] else False for coin in coins}

while True:
    now = datetime.datetime.now()

    # 매도 시도
    if now.hour == 8 and now.minute == 59 and 50 <= now.second <= 59:
        for coin in coins:
            try:
                if op_modes[f"KRW-{coin}"] is True and holds[f"KRW-{coin}"] is True:
                    coin_balance = upbit.get_balance(f"KRW-{coin}")
                    upbit.sell_market_order(f"KRW-{coin}", coin_balance)
                    holds[f"KRW-{coin}"] = False

                op_modes[f"KRW-{coin}"] = False
            except Exception as e:
                logging.error(f"매도 주문 중 오류 발생: {coin}: {e}")

        time.sleep(10)

    # 09:00:00 목표가 갱신
    if now.hour == 9 and now.minute == 0 and 20 <= now.second <= 30:
        for coin in coins:
            try:
                targets[f"KRW-{coin}"] = cal_target(f"KRW-{coin}")
                op_modes[f"KRW-{coin}"] = True
            except Exception as e:
                logging.error(f"목표가 갱신 중 오류 발생: {coin}: {e}")

    for coin in coins:
        try:
            price = pyupbit.get_current_price(f"KRW-{coin}")

            # 매초마다 조건을 확인한 후 매수 시도
            if op_modes[f"KRW-{coin}"] is True and price is not None and price >= targets[f"KRW-{coin}"] and holds[f"KRW-{coin}"] is False:
                # 매수
                krw_balance = upbit.get_balance("KRW")
                upbit.buy_market_order(f"KRW-{coin}", krw_balance * 0.3)
                holds[f"KRW-{coin}"] = True

            # 상태 출력
            logging.info(f"현재 시간:{now} 코인: {coin} 목표 가격: {targets[f'KRW-{coin}']} 현재 가격: {price} 보유 상태: {holds[f'KRW-{coin}']} 운영 상태: {op_modes[f'KRW-{coin}']}")
        except Exception as e:
            logging.error(f"메인 루프 중 오류 발생: {coin}: {e}")

    time.sleep(1)
    try:
        # KeyboardInterrupt 처리
        pass
    except KeyboardInterrupt:
        logging.info("프로그램을 종료합니다.")
        break
    except Exception as e:
        logging.error(f"예외적인 오류 발생: {e}")