import json
import logging
import threading
import time
from threading import Thread

import websocket
from channels.generic.websocket import WebsocketConsumer

from apps.utils import ExchangeService
from apps.utils import normalize_pair

logger = logging.getLogger(__name__)

real_time_prices = {
    'binance': {},
    'kraken': {}
}

price_lock = threading.Lock()

BINANCE_CHUNK_SIZE = 100
KRAKEN_CHUNK_SIZE = 100
PING_INTERVAL = 15
MAX_RECONNECT_ATTEMPTS = 10


class CryptoWebSocketConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        binance_pairs = ExchangeService.get_binance_pairs()
        kraken_pairs = ExchangeService.get_kraken_pairs()

        binance_pairs = [normalize_pair(pair) for pair in binance_pairs]
        kraken_pairs = [normalize_pair(pair) for pair in kraken_pairs]

        binance_chunks = [
            binance_pairs[i:i + BINANCE_CHUNK_SIZE] for i in range(0, len(binance_pairs), BINANCE_CHUNK_SIZE)
        ]

        for chunk in binance_chunks:
            thread = Thread(target=self.connect_binance, args=(chunk,))
            thread.start()
            time.sleep(2)

        kraken_chunks = [kraken_pairs[i:i + KRAKEN_CHUNK_SIZE] for i in range(0, len(kraken_pairs), KRAKEN_CHUNK_SIZE)]

        for chunk in kraken_chunks:
            thread = Thread(target=self.connect_kraken, args=(chunk,))
            thread.start()
            time.sleep(2)

    def connect_binance(self, pairs):
        binance_streams = [f"{pair.lower().replace('/', '')}@ticker" for pair in pairs]
        streams = '/'.join(binance_streams)
        ws_url = f'wss://stream.binance.com:9443/ws/{streams}'

        logger.info(f"Connecting to Binance WebSocket for {len(pairs)} pairs.")

        websocket_app = websocket.WebSocketApp(
            url=ws_url,
            on_message=self.process_binance_data,
            on_error=self.on_ws_error,
            on_close=self.on_ws_close
        )
        websocket_app.run_forever()

    def connect_kraken(self, pairs, attempt=0):
        if attempt > MAX_RECONNECT_ATTEMPTS:
            logger.error(f"Max reconnection attempts reached for Kraken pairs: {pairs}")
            return

        def on_open(ws):
            logger.info(f"Subscribing to {len(pairs)} Kraken pairs.")
            self.kraken_subscribe(ws, pairs)

        def on_message(ws, message):
            data = json.loads(message)
            if 'event' in data and data['event'] == 'heartbeat':
                logger.info("Heartbeat received from Kraken WebSocket.")

            self.process_kraken_data(ws, message)

        websocket_app = websocket.WebSocketApp(
            url='wss://ws.kraken.com',
            on_message=on_message,
            on_open=on_open,
            on_error=self.on_ws_error,
            on_close=lambda ws, close_status_code, close_msg: self.on_ws_close
            (ws, close_status_code, close_msg, pairs, attempt),
        )

        logger.info(f"Connecting to Kraken WebSocket for {len(pairs)} pairs.")

        ping_thread = Thread(target=self.kraken_ping_pong, args=(websocket_app,))
        ping_thread.start()

        websocket_app.run_forever()

    @staticmethod
    def on_ws_error(ws, error):
        logger.error(f"WebSocket error: {error}")

    def on_ws_close(self, ws, close_status_code, close_msg, pairs=None, attempt=0):
        logger.warning(
            f"WebSocket closed: {close_msg} (Code: {close_status_code}). Reconnecting in {5 * attempt} seconds...")
        time.sleep(5 * attempt)
        if pairs:
            self.connect_kraken(pairs, attempt + 1)  # Reconnect for Kraken

    @staticmethod
    def kraken_subscribe(ws, pairs):
        max_chunk_size = 100  # To avoid hitting Kraken's subscription limits, chunk the pairs
        chunked_pairs = [pairs[i:i + max_chunk_size] for i in range(0, len(pairs), max_chunk_size)]

        for chunk in chunked_pairs:
            logger.info(f"Subscribing to Kraken pairs: {chunk}")
            subscribe_message = {
                "event": "subscribe",
                "pair": chunk,
                "subscription": {"name": "ticker"},
            }
            ws.send(json.dumps(subscribe_message))

    def process_binance_data(self, ws, message):
        data = json.loads(message)
        avg_price = (float(data['b']) + float(data['a'])) / 2
        normalized_pair = normalize_pair(data['s'])

        real_time_prices['binance'][normalized_pair] = avg_price

        self.send(text_data=json.dumps({
            'exchange': 'binance',
            'pair': normalized_pair,
            'price': avg_price,
        }))

    def process_kraken_data(self, ws, message):
        try:
            data = json.loads(message)

            if 'event' in data and data['event'] == 'systemStatus':
                logger.info(f"Kraken system status: {data}")
                return

            if 'event' in data and data['event'] == 'subscriptionStatus' and 'status' in data:
                if data['status'] == 'error':
                    logger.warning(f"Kraken subscription error: {data['errorMessage']} for pair: {data['pair']}")
                return

            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], dict):
                avg_price = (float(data[1]['b'][0]) + float(data[1]['a'][0])) / 2
                normalized_pair = normalize_pair(data[3])

                with price_lock:
                    real_time_prices['kraken'][normalized_pair] = avg_price
                    logger.info(f"Updated Kraken price for {normalized_pair}: {avg_price}")

                self.send(text_data=json.dumps(
                    {
                        'exchange': 'kraken',
                        'pair': normalized_pair,
                        'price': avg_price,
                    }
                ))
            else:
                logger.warning(f"Unexpected message structure from Kraken: {message}")
        except Exception as e:
            logger.error(f"Error processing Kraken message: {e}")

    @staticmethod
    def kraken_ping_pong(ws):
        while ws.sock and ws.sock.connected:
            try:
                ws.send(json.dumps({'event': 'ping'}))
                logger.info('Ping sent to Kraken WebSocket.')
                time.sleep(PING_INTERVAL)
            except Exception as e:
                logger.error(f"Error during ping: {e}")
                break

    @staticmethod
    def on_pong():
        logger.info("Pong received from Kraken WebSocket.")
