# Overview
The Crypto Real-Time Price API is a Django-based API service that retrieves real-time cryptocurrency price data from multiple exchanges, including Binance and Kraken, through WebSocket connections. This API allows users to fetch price data for specific trading pairs or all pairs available from the exchanges.

## Features
*  Real-time cryptocurrency price data using WebSocket connections.
*  Supports Binance and Kraken exchanges.
*  Fetch prices for specific trading pairs or all available pairs.
*  API filtering with parameters for pair and exchange.
* No database is required, all data is stored in memory.
* Dockerized for easy deployment.

## Project Structure
*  consumers.py: Handles WebSocket connections and processes data from the exchanges.
*  views.py: Implements the API endpoint to fetch prices.
*  utils.py: Contains utility functions for normalizing and fetching data.
*  strategies: Logic to fetch and subscribe WebSockets for supported pairs.

#### To make the process easier, Docker is used to build and run the application in a containerized environment.
Step 1 `docker-compose build`

Step 2 `docker-compose up`

Step 3 `http://localhost:8001` and `ws://localhost:8001/ws/crypto/`

Also check your logs.

#### The API can be accessed through the following endpoints:

Fetch All Prices:
GET /api/prices/
Returns price data for all trading pairs across all exchanges.

Fetch Prices for a Specific Exchange:
GET /api/prices/?exchange=binance
Returns all trading pairs for the specified exchange.

Fetch Prices for a Specific Pair Across All Exchanges:
GET /api/prices/?pair=ZEC/ETH
Searches across all exchanges for the specified pair and returns price data.

Fetch Prices for a Specific Pair on a Specific Exchange:
GET /api/prices/?pair=BTC/USDT&exchange=binance
Returns the price of the specified pair on the specified exchange.
