import logging

import requests

logger = logging.getLogger(__name__)


class ExchangeService:
    BINANCE_API_URL = 'https://api.binance.com/api/v3/exchangeInfo'
    KRAKEN_API_URL = 'https://api.kraken.com/0/public/AssetPairs'

    @classmethod
    def get_binance_pairs(cls):
        try:
            response = requests.get(cls.BINANCE_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            binance_pairs = []
            for symbol_info in data.get('symbols', []):
                base_asset = symbol_info.get('baseAsset')
                quote_asset = symbol_info.get('quoteAsset')
                if base_asset and quote_asset:
                    pair = f"{base_asset}/{quote_asset}"
                    binance_pairs.append(pair)

            logger.info(f"Fetched {len(binance_pairs)} pairs from Binance")
            return binance_pairs

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Binance pairs: {e}")
            return []

    @classmethod
    def get_kraken_pairs(cls):
        try:
            response = requests.get(cls.KRAKEN_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'error' in data and data['error']:
                logger.error(f"Error fetching supported Kraken pairs: {data['error']}")
                return []

            return list(data['result'].keys())
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Kraken pairs: {e}")
            return []


def normalize_pair(pair):
    pair = pair.upper()
    if '/' not in pair and '_' not in pair:
        base = pair[:-3]
        quote = pair[-3:]
        return f"{base}/{quote}"

    return pair.replace('_', '/')
