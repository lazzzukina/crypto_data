from django.http import JsonResponse
from django.views import View

from apps.consumers import real_time_prices
from apps.utils import normalize_pair


class CryptoPriceAPIView(View):
    def get(self, request, *args, **kwargs):
        pair = request.GET.get('pair', None)
        exchange = request.GET.get('exchange', None)

        if not real_time_prices:
            return JsonResponse({'error': 'No price data available.'}, status=400)

        filtered_data = {}

        exchange = exchange.lower() if exchange else None

        match (pair, exchange):
            case (None, None):
                filtered_data = real_time_prices

            case (None, exchange):
                if exchange in real_time_prices:
                    filtered_data[exchange] = real_time_prices[exchange]
                else:
                    return JsonResponse({'error': f'No data found for exchange: {exchange}'}, status=404)

            case (pair, None):
                normalized_pair = normalize_pair(pair)

                for ex, pairs in real_time_prices.items():
                    for stored_pair in pairs.keys():
                        if stored_pair == normalized_pair:
                            if ex not in filtered_data:
                                filtered_data[ex] = {}
                            filtered_data[ex][stored_pair] = pairs[stored_pair]

                if not filtered_data:
                    return JsonResponse({'error': f'No data found for pair: {pair} on any exchange'}, status=404)

            case (pair, exchange):
                normalized_pair = normalize_pair(pair)
                if exchange in real_time_prices and normalized_pair in real_time_prices[exchange]:
                    filtered_data[exchange] = {normalized_pair: real_time_prices[exchange][normalized_pair]}
                else:
                    return JsonResponse(
                        {'error': f'No data found for pair: {pair} on exchange: {exchange}'},
                        status=404,
                    )

        return JsonResponse(filtered_data)
