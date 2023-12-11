from .constants import *
from .models import *


def reverse(side: str) -> str:
    return SIDE_SELL if side == SIDE_BUY else SIDE_BUY


def signature(position: Position) -> str:
    return f'{position.symbol}_{position.side}'


def dummy_pos(symbol, side, size=Decimal(0), leverage=Decimal(1)) -> Position:
    return Position(
        symbol,
        side,
        Decimal(0),
        size,
        datetime.now(),
        leverage,
        'me'
    )
