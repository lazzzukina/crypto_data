import json

import websocket

from apps.strategies.exchange_strategy import ExchangeStrategy


class BinanceStrategy(ExchangeStrategy):
    def connect(self, pairs):
        binance_pairs = [pair.lower().replace('/', '').replace('_', '') for pair in pairs]
        streams = '/'.join([f"{pair}@ticker" for pair in binance_pairs])
        ws_url = f'wss://stream.binance.com:9443/ws/{streams}'
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.process_message,
        )
        ws.run_forever()

    def subscribe(self, ws, pairs):
        pass

    def process_message(self, ws, message):
        data = json.loads(message)
        avg_price = (float(data['b']) + float(data['a'])) / 2

        return {
            'exchange': 'binance',
            'pair': data['s'],
            'price': avg_price,
        }
