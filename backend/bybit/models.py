from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class Position:
    symbol: str
    side: str
    entry_price: Decimal
    closed_price: Decimal | None
    size: Decimal
    open_at: datetime
    created_at: datetime
    closedAt: datetime | None
    leverage: Decimal
    creator: str


@dataclass
class Order:
    symbol: str
    side: str
    entry_price: Decimal
    size: Decimal
    created_at: datetime
    transact_time: datetime


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
