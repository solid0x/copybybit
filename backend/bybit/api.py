import requests

from pybit.unified_trading import HTTP
from urllib.parse import quote

from .constants import *
from .models import *


class BybitAPI:

    def __init__(self, api_key=None, api_secret=None, use_testnet=True):
        self.http = HTTP(api_key=api_key, api_secret=api_secret, testnet=use_testnet)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USERAGENT})

    def get_wallet_balance(self):
        return self.http.get_wallet_balance(accountType=ACCOUNT_TYPE_UNIFIED)['result']['list'][0]

    def get_coin_balance(self, coin='USDT') -> CoinBalance:
        wallet = self.get_wallet_balance()
        coins = {c['coin']: CoinBalance(c['coin'], Decimal(c['equity']), Decimal(c['walletBalance']))
                 for c in wallet['coin']}
        return coins.get(coin)

    def get_ticker(self, symbol, category=CATEGORY_LINEAR) -> Ticker:
        ticker = self.http.get_tickers(category=category, symbol=symbol)['result']['list'][0]
        return Ticker(
            symbol,
            Decimal(ticker['lastPrice']),
            Decimal(ticker['indexPrice']),
            Decimal(ticker['markPrice']),
            Decimal(ticker['fundingRate'])
        )

    def get_instruments_info(self, category=CATEGORY_LINEAR) -> dict[str, InstrumentInfo]:
        instruments_info = self.http.get_instruments_info(category=category)['result']['list']
        return {
            i['symbol']: InstrumentInfo(
                i['symbol'],
                Decimal(i['lotSizeFilter']['minOrderQty']),
                Decimal(i['lotSizeFilter']['maxOrderQty']),
                Decimal(i['lotSizeFilter']['qtyStep']),
                Decimal(i['leverageFilter']['minLeverage']),
                Decimal(i['leverageFilter']['maxLeverage']),
                Decimal(i['leverageFilter']['leverageStep'])
            ) for i in instruments_info
        }

    def get_position_info(self, symbol, side, category=CATEGORY_LINEAR) -> PositionInfo:
        response = self.http.get_positions(symbol=symbol, category=category)['result']['list']
        position_idx = HEDGE_MODE_BUY if side == SIDE_BUY else HEDGE_MODE_SELL
        position_info = [p for p in response if p['positionIdx'] == position_idx][0]

        leverage = self.get_decimal(position_info['leverage'])
        avg_price = self.get_decimal(position_info['avgPrice'])
        mark_price = self.get_decimal(position_info['markPrice'])
        size = self.get_decimal(position_info['size'])
        unrealised_pnl = self.get_decimal(position_info['unrealisedPnl'])

        return PositionInfo(
            symbol,
            side,
            leverage,
            avg_price,
            mark_price,
            size,
            unrealised_pnl,
        )

    def get_positions_info(self, category=CATEGORY_LINEAR) -> list[PositionInfo]:
        result: list[PositionInfo] = []
        positions_info = self.http.get_positions(settleCoin='USDT', category=category)['result']['list']

        for position_info in positions_info:
            symbol = position_info['symbol']
            side = position_info['side']
            leverage = self.get_decimal(position_info['leverage'])
            avg_price = self.get_decimal(position_info['avgPrice'])
            mark_price = self.get_decimal(position_info['markPrice'])
            size = self.get_decimal(position_info['size'])
            unrealised_pnl = self.get_decimal(position_info['unrealisedPnl'])

            result.append(PositionInfo(
                symbol,
                side,
                leverage,
                avg_price,
                mark_price,
                size,
                unrealised_pnl,
            ))

        return result

    def set_leverage(self, symbol, leverage, category=CATEGORY_LINEAR):
        return self.http.set_leverage(symbol=symbol, category=category,
                                      buyLeverage=str(leverage), sellLeverage=str(leverage))

    def place_order(self, symbol, side, order_type, qty, price='',
                    category=CATEGORY_LINEAR, position_idx=ONE_WAY_MODE):
        return self.http.place_order(
            category=category,
            symbol=symbol,
            side=side,
            orderType=order_type,
            qty=qty,
            price=price,
            positionIdx=position_idx
        )['result']

    @staticmethod
    def get_decimal(value, default=Decimal(0)) -> Decimal:
        if value:
            return Decimal(value)
        return default


class BybitLeadersAPI:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USERAGENT})
        self.http_get(PUBLIC_BASE_URL)

    def http_get(self, url, params=None):
        return self.session.get(url, params=params, timeout=10)

    def get_leader_list(self, duration=DURATION_30D, count=100) -> list[str]:
        leaders = []
        page = 1

        while len(leaders) < count:
            url = f'{PUBLIC_BASE_URL}/common/dynamic-leader-list'
            result = self.http_get(url, {
                'pageNo': page,
                'pageSize': 50,
                'sortType': 'SORT_TYPE_DESC',
                'dataDuration': duration,
                'sortField': 'LEADER_SORT_FIELD_SORT_ROI',
            }).json()['result']

            for leader in result['leaderDetails']:
                leaders.append(leader['leaderMark'])

            page += 1

        return leaders[:count]

    def get_leader_positions(self, mark) -> list[Position]:
        positions = []
        url = f'{PUBLIC_BASE_URL}/common/position/list'
        result = self.http_get(url, {
            'leaderMark': quote(mark),
        }).json()['result']['data']

        for p in result:
            positions.append(Position(
                p['symbol'],
                p['side'],
                Decimal(p['entryPrice']),
                Decimal(p['sizeX']) / 10 ** 8,
                datetime.now(),
                Decimal(p['leverageE2']) / 100,
                mark
            ))

        return positions
