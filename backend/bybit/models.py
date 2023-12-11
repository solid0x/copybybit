from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class Position:
    symbol: str
    side: str
    entry_price: Decimal
    size: Decimal
    open_at: datetime
    leverage: Decimal
    creator: str


@dataclass
class PositionInfo:
    symbol: str
    side: str
    leverage: Decimal
    avg_price: Decimal
    mark_price: Decimal
    size: Decimal
    unrealised_pnl: Decimal


@dataclass
class CoinBalance:
    coin: str
    equity: Decimal
    balance: Decimal


@dataclass
class InstrumentInfo:
    symbol: str
    min_order_qty: Decimal
    max_order_qty: Decimal
    qty_step: Decimal
    min_leverage: Decimal
    max_leverage: Decimal
    leverage_step: Decimal


@dataclass
class Ticker:
    symbol: str
    last_price: Decimal
    index_price: Decimal
    mark_price: Decimal
    funding_rate: Decimal
