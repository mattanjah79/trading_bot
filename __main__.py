import queue
import numpy as np
from datetime import datetime

import note
import API
from app import refresh_price
from ichimoku import df
import time
import os
from API import XTB
from queue import LifoQueue

data = XTB(note.user_['login'], note.user_['password'])
symbol = "USDJPY"
back_26_date = "2022-10-12"
reference_date = "2022-11-18"
volume = 0.01
buffor = 1

clear = lambda: os.system('cls')

def looking_for_signals():

    bl5 = []  # buy last five-teen
    sl5 = []  # sell last five-teen
    close = []
    open = {"num": 0,
            "param": []}

    bl_sig3th = 0
    bl_sig4th = 0
    bl_sig5th = 0
    buy_signal = 0
    sl_sig3th = 0
    sl_sig4th = 0
    sl_sig5th = 0
    sell_signal = 0
    loop_refresh = 30
    loop = True
    value = 0
    while loop:
        print(f'Loop refresh: {loop_refresh}')
        print(buy_signal, sell_signal)
        if sell_signal >= 1 and open['num'] < 3:
            trade = data.make_Trade(symbol, 1, 0, volume)
            print(trade)
            sell_signal = 0
            open['num'] += 1
            open['param'].append(trade)

        if buy_signal >= 1 and open['num'] < 3:
            trade = data.make_Trade(symbol, 0, 0, volume)
            print(trade)
            buy_signal = 0
            open['num'] += 1
            open['param'].append(trade)

        if open['num'] > 0:
            order_number = data.getTrades()
            loop = False
            return open['param'][0][1], open['param'][0][2], order_number[0]['order']
        else:
            print(f"Iter {value}")

        buy = refresh_price(symbol, data)['buy']
        if bl5:
            if buy > bl5[0]:
                bl5.insert(0, buy)
            else:
                if buy < np.mean(bl5)*buffor:
                    bl5.clear()
                else:
                    print(np.mean(bl5)*buffor)
        else:
            bl5.insert(0, buy)

        sell = refresh_price(symbol, data)['sell']
        if sl5:
            if sell < sl5[0]:
                sl5.insert(0, sell)
            else:
                if sell > np.mean(sl5)*buffor:
                    sl5.clear()
                else:
                    print(np.mean(sl5)*buffor)
        else:
            sl5.insert(0, sell)

        value += 1

        if len(bl5) < 4:
            loop_refresh = 30
        else:
            loop_refresh = 15
        if len(bl5) == 3:
            bl_sig3th += 1
        elif len(bl5) == 4:
            bl_sig4th += 1
        elif len(bl5) == 5:
            bl_sig5th += 1
        elif len(bl5) >= 6:
            buy_signal += 1

            bl_sig3th = 0
            bl_sig4th = 0
            bl_sig5th = 0

        if len(sl5) < 4:
            loop_refresh = 30
        else:
            loop_refresh = 15
        if len(sl5) == 3:
            sl_sig3th += 1

        elif len(sl5) == 4:
            sl_sig4th += 1
        elif len(sl5) == 5:
            sl_sig5th += 1
        elif len(sl5) >= 6:
            sell_signal += 1
            sl_sig3th = 0
            sl_sig4th = 0
            sl_sig5th = 0

        print(f"Buy list: {len(bl5)}", bl5)
        print(f"Sell list: {len(sl5)}", sl5)
        signals = {
            'buy':
                {
                    "buy_3": bl_sig3th,
                    "buy_4": bl_sig4th,
                    "buy_5": bl_sig5th
                    },
            'sell':
                {
                    "sell_3": sl_sig3th,
                    "sell_4": sl_sig4th,
                    "sell_5": sl_sig5th
                }
        }

        time.sleep(loop_refresh)
        clear()



def manage_transaction(trans, cmd, order):

    loop = True
    take_profit = -1.0
    step_profit = 0.5
    while loop:
        time.sleep(1)
        clear()
        balance = data.get_Balance()
        prize = (balance['equity'] - balance['balance'])
        print(f'Prize: {prize}')
        print(f'Take profit on: {take_profit}')
        print(f'Next step profit on: {step_profit}')
        if prize < take_profit:
            close = data.make_Trade(symbol=symbol, cmd=cmd, transaction_type=2, volume=volume, order=order)
            loop = False
        elif prize > step_profit:
            time.sleep(1)
            take_profit += 1.0
            step_profit += 1.5
        else:
            pass



def main():
    loop = True
    while loop:
        time.sleep(1)
        trans = looking_for_signals()
        time.sleep(2)
        now = datetime.now()
        print(f'Transaction {trans[2]} was open at {now.strftime("%d/%m/%Y %H:%M:%S")}.')
        manage_transaction(trans[0], trans[1], trans[2])
        now = datetime.now()
        print(f'Transaction {trans[2]} was closed as {now.strftime("%d/%m/%Y %H:%M:%S")}.')
        clear()

if __name__ == "__main__":
    main()

























"""first = {}
    secound = {}

    print("Close: ",df.loc[reference_date]['Close'])
    print("tenken sen", df.loc[reference_date]['tenkan_sen'])
    print("kijun sen", df.loc[reference_date]['kijun_sen'])
    print("senkou span a", df.loc[reference_date]['senkou_span_a'])
    print("senkou span b", df.loc[reference_date]['senkou_span_b'])
    print(f"chikou_span {back_26_date}", df.loc[back_26_date]['chikou_span'])
    print(refresh_price(symbol))
    balance = API.get_Balance()
    print(balafddgdsfgdnace)
    API.logout()
        """

