import dataclasses
import pybit.exceptions
import logging

from bybit.api import *
from bybit.utils import *


ERROR_CODE_REDUCE_ONLY_NOT_SATISFIED = 110017


class TradeService:

    def __init__(self, api_key: str, api_secret: str):
        self.api = BybitAPI(api_key, api_secret, use_testnet=True)
        self.instruments: dict[str, InstrumentInfo] = {}
        self.load_instruments()

    def load_instruments(self):
        self.instruments = self.api.get_instruments_info()

    def get_equity(self):
        return self.api.get_coin_balance().equity

    def get_qty(self, symbol: str, cost: Decimal, price: Decimal = None, leverage: Decimal = 1) -> Decimal | None:
        if symbol in self.instruments:
            instrument = self.instruments[symbol]
            if instrument.min_leverage <= leverage <= instrument.max_leverage:
                if not price:
                    ticker = self.api.get_ticker(symbol)
                    price = ticker.mark_price

                qty_raw = cost / price * leverage
                qty_step = instrument.qty_step
                if qty_step < 1:
                    qty = qty_raw.quantize(qty_step)
                else:
                    qty = round(qty_raw / qty_step) * qty_step

                if instrument.min_order_qty <= qty <= instrument.max_order_qty:
                    return qty
                else:
                    logging.warning(f"Calculated qty {qty} ({qty_raw}) doesn't fit bounds "
                                    f"from {instrument.min_order_qty} to {instrument.max_order_qty}")
            else:
                logging.warning(f"Leverage {leverage}x doesn't fit bounds {symbol} instrument "
                                f"from {instrument.min_leverage} to {instrument.max_leverage}")
        else:
            logging.warning(f'Instrument for symbol {symbol} not found')

        return None

    def update_leverage(self, symbol: str, side: str, leverage: Decimal):
        position_info = self.api.get_position_info(symbol, side)
        if position_info.leverage != leverage:
            self.api.set_leverage(symbol, leverage)

    def get_position_info(self, position: Position) -> PositionInfo:
        return self.api.get_position_info(position.symbol, position.side)

    def get_open_positions(self) -> list[PositionInfo]:
        return self.api.get_positions_info()

    def place_order(self, symbol: str, side: str, price: Decimal, cost: Decimal, leverage: Decimal):
        position = dummy_pos(symbol, side)

        position_idx = self.get_position_idx(position)
        qty = self.get_qty(symbol, price, cost)

        if qty:
            self.update_leverage(symbol, side, leverage)
            self.api.place_order(symbol, side, ORDER_TYPE_LIMIT, qty, str(price), position_idx=position_idx)
            logging.info(f'{self.label(position)} order placed with {qty} qty')
        else:
            logging.warning(f'Position {self.label(position)} is not open')

    def open_position(self, position: Position, cost: Decimal):
        position_idx = self.get_position_idx(position)
        qty = self.get_qty(position.symbol, cost, leverage=position.leverage)

        if qty:
            self.update_leverage(position.symbol, position.side, position.leverage)
            self.api.place_order(position.symbol, position.side, ORDER_TYPE_MARKET, qty, position_idx=position_idx)
            logging.info(f'{self.label(position)} opened with {qty} qty')
        else:
            logging.warning(f'Position {self.label(position)} is not open')

    def close_position(self, position: Position):
        qty = self.get_position_info(position).size

        if qty:
            position_idx = self.get_position_idx(position)
            try:
                self.api.place_order(position.symbol, reverse(position.side), ORDER_TYPE_MARKET, qty,
                                     position_idx=position_idx)
                logging.info(f'{self.label(position)} with {qty} qty closed')
            except pybit.exceptions.InvalidRequestError as e:
                logging.exception(f"Position wasn't closed due to invalid request: {e}")
                if e.status_code == ERROR_CODE_REDUCE_ONLY_NOT_SATISFIED:
                    logging.warning(f'Position {self.label(position)} could be liquidated')
                raise e
        else:
            logging.warning(f"Position for {position.symbol} wasn't open or liquidated")

    @staticmethod
    def reverse(position: Position) -> Position:
        new_side = SIDE_BUY if position.side == SIDE_SELL else SIDE_SELL
        return dataclasses.replace(position, side=new_side)

    @classmethod
    def label(cls, position: Position) -> str:
        return cls.pretty_print(position.side, position.symbol)

    @staticmethod
    def pretty_print(side: str, symbol: str) -> str:
        side_mark = '🟩' if side == SIDE_BUY else '🟥'
        return f'{side_mark}{symbol}'

    @staticmethod
    def get_position_idx(position: Position) -> str:
        return HEDGE_MODE_BUY if position.side == SIDE_BUY else HEDGE_MODE_SELL
