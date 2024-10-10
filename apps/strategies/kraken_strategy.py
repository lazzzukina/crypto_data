import json
import logging

import websocket

from apps.strategies.exchange_strategy import ExchangeStrategy
from apps.utils import ExchangeService

logger = logging.getLogger(__name__)


class KrakenStrategy(ExchangeStrategy):
    def connect(self, pairs):
        supported_pairs = ExchangeService.get_kraken_pairs()

        if not supported_pairs:
            logger.error('No supported pairs fetched from Kraken. Aborting connection.')
            return

        valid_pairs = [pair for pair in pairs if pair.replace('_', '/') in supported_pairs]

        if not valid_pairs:
            logger.error('No valid pairs to subscribe to after filtering unsupported pairs.')
            return

        ws_url = 'wss://ws.kraken.com'
        websocket_app = websocket.WebSocketApp(
            url=ws_url,
            on_message=self.process_message,
            on_open=lambda ws: self.subscribe(ws, valid_pairs),
        )
        websocket_app.run_forever()

    def subscribe(self, ws, pairs):
        normalized_pairs = [pair.replace('_', '/') for pair in pairs]
        subscribe_message = {
            'event': 'subscribe',
            'pair': normalized_pairs,
            'subscription': {'name': 'ticker'},
        }
        ws.send(json.dumps(subscribe_message))

    def process_message(self, ws, message):
        data = json.loads(message)

        match data:
            case {'event': 'subscriptionStatus', 'status': 'error', 'errorMessage': error_msg, 'pair': pair}:
                logger.warning(f"Subscription error: {error_msg} for pair: {pair}")

            case {'event': 'systemStatus'}:
                logger.info(f"System status: {data}")

            case list() if len(data) > 1 and isinstance(data[1], dict):
                avg_price = (float(data[1]['b'][0]) + float(data[1]['a'][0])) / 2
                return {
                    'exchange': 'kraken',
                    'pair': data[3],
                    'price': avg_price,
                }

            case _:
                logger.warning(f"Unexpected message structure from Kraken: {message}")
