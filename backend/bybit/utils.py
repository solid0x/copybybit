from .constants import *
from .models import *


def reverse(side: str) -> str:
    return SIDE_SELL if side == SIDE_BUY else SIDE_BUY


def signature(position: Position) -> str:
    return f'{position.symbol}_{position.side}'


def short_desc(position: Position):
    side_mark = '🟩' if position.side == SIDE_BUY else '🟥'
    total = position.entry_price * position.size
    return f'{side_mark}{position.symbol} {position.entry_price:.2f} {total:.2f}$'


def dummy_pos(symbol, side, size=Decimal(0), leverage=Decimal(1)) -> Position:
    return Position(
        symbol,
        side,
        Decimal(0),
        None,
        size,
        datetime.now(),
        datetime.now(),
        None,
        leverage,
        'me'
    )
