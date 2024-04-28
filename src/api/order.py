import os
import time
import random
import math
import requests
import json
import logging

logging.basicConfig(filename= 'trade.log', level=logging.INFO, format='[%(asctime)s - %(levelname)s - %(message)s]')

from typing import List, Dict, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from utils import now, create_signature

order_router = APIRouter(prefix="/order")
api_domain = "https://api-glb.hashkey.com"

@order_router.post("/create", response_model=Any)
async def create(
    symbol: str = Query(..., description="symbol of the trading pair", examples="ETHUSD"),
    side: str = Query(..., description="side of the order, BUY or SELL", examples="BUY"),
    type: str = Query(..., description="type of the order, LIMIT or MARKET", examples="LIMIT"),
    quantity: float = Query(..., description="quantity of the order", examples=0.01),
    amount: float = Query(..., description="amount of the order. market order only", examples=1800),
    price: float = Query(..., description="price of the order", examples=1800),
    newClientOrderId: str = Query("1234567890", description="unique order ID", examples="1234567890"),
    timeInForce: str = Query("GTC", description="time in force", examples="GTC"),
):
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)

    url = f"{api_domain}/api/v1/spot/order?"
    params = ""
    if type == "MARKET" and side == "BUY": # market order
        params = f"symbol={symbol}&side={side}&type=MARKET&quantity={quantity}"
    elif type == "MARKET" and side == "SELL": # market order
        params = f"symbol={symbol}&side={side}&type=MARKET&quantity={quantity}"
    elif type == "LIMIT" and side == "BUY": # limit order
        params = f"symbol={symbol}&side={side}&type=LIMIT&quantity={quantity}&price={price}"
    elif type == "LIMIT" and side == "SELL": # limit order
        params = f"symbol={symbol}&side={side}&type=LIMIT&quantity={quantity}&price={price}"
    params += f"&recWindow=5000&timestamp={timestamp}"
    signature = create_signature(secret_key, params)
    params += f"&signature={signature}"
    
    url += params
    
    # import pdb; pdb.set_trace()
    headers = {
        "accept": "application/json",
        "X-HK-APIKEY": access_key    
    }

    try:
        response = requests.post(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        return {"status": "error", "message": "request error"}

    print(response.text)
    return response.json()

@order_router.get("/open-orders", response_model=List[Optional[Dict]])
async def open_orders():
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)
    
    url = f"{api_domain}/api/v1/spot/openOrders?"
    params= f"recvWindow=5000&timestamp={timestamp}"
    signature = create_signature(secret_key, params)
    params += f"&signature={signature}"
    url += params
    
    headers = {
        "accept": "application/json",
        "X-HK-APIKEY": access_key    
    }
    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        print(e)
        return {"status": "error", "message": "request error"}

    return response.json()

@order_router.get("/balance", response_model=Any)
async def balance():
    account_id = 1669868710955865344
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)

    url = f"{api_domain}/api/v1/account?"
    params = f"accountId={account_id}&recvWindow=5000&timestamp={timestamp}"
    signature = create_signature(secret_key, params)
    params += f"&signature={signature}"
    url += params

    headers = {
        "accept": "application/json",
        "X-HK-APIKEY": access_key
    }

    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        print(e)
        return {"status": "error", "message": "request error"}

    return response.json()

@order_router.post("/buy-market", response_model=Any)
async def buy_market():
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)

    try:
        order = await create(
            symbol="BTCUSDT",
            side="BUY",
            type="MARKET",
            quantity=5000,
            timeInForce="IOC"
        )
    except Exception as e:
        return {"status": "error", "message": "request error"}
    
    return order

@order_router.post("/buy-limit", response_model=Any)
async def buy_limit(
    symbol: str = Query("BTCUSDT", description="symbol of the trading pair", examples="BTCUSDT"),
    price: float = Query(..., description="price of the order", examples=1800),
    quantity: float = Query(..., description="quantity of the order", examples=0.01)
):
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)

    try:
        order = await create(
            symbol=symbol,
            price=price,
            quantity=quantity,
            side="BUY",
            type="LIMIT",
            timeInForce="GTC"
        )
    except Exception as e:
        return {"status": "error", "message": "request error"}
    
    return order

@order_router.post("/sell-market", response_model=Any)
async def sell_market():
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)

    try:
        balances = (await balance())["balances"]
        btc_balance = 0
        for asset in balances:
            if asset["asset"] == "BTC":
                btc_balance = asset["free"]
                btc_balance = math.floor(float(btc_balance) * 100000) / 100000
                break
        
        order = await create(
            symbol="BTCUSDT",
            side="SELL",
            type="MARKET",
            quantity=btc_balance,
            timeInForce="IOC"
        )
    except Exception as e:
        return {"status": "error", "message": "request error"}
    
    return order

@order_router.post("/sell-limit", response_model=Any)
async def sell_limit(
    symbol: str = Query("BTCUSDT", description="symbol of the trading pair", examples="BTCUSDT"),
    price: float = Query(..., description="price of the order", examples=1800),
    quantity: float = Query(..., description="quantity of the order", examples=0.01)
):
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)
    try:
        order = await create(
            symbol=symbol,
            price=price,
            quantity=quantity,
            side="SELL",
            type="LIMIT",
            timeInForce="GTC"
        )
    except Exception as e:
        return {"status": "error", "message": "request error"}
    
    return order

@order_router.delete("/cancel-orders-all", response_model=Any)
async def cancel_orders_all():
    access_key, secret_key = os.getenv("HASHKEY_ACCESS_KEY"), os.getenv("HASHKEY_SECRET_KEY")
    timestamp = now("millisecond", 9)

    url = f"{api_domain}/api/v1/spot/openOrders?"
    params = f"timestamp={timestamp}"
    signature = create_signature(secret_key, params)
    params += f"&signature={signature}"
    url += params
    
    headers = {
        "accept": "application/json",
        "X-HK-APIKEY": access_key    
    }

    try:
        response = requests.delete(url, headers=headers)
    except Exception as e:
        print(e)
        return {"status": "error", "message": "request error"}
    
    return response.json()

@order_router.get("/get-orderbook", response_model=Any)
async def get_orderbook(
    symbol: str = Query("BTCUSDT", description="symbol of the trading pair", examples="BTCUSDT"),
    limit: int = Query(5, description="limit of the orderbook", examples=5)
):
    url = f"{api_domain}/quote/v1/depth?symbol={symbol}&limit={limit}"
    try:
        response = requests.get(url)
    except Exception as e:
        print(e)
        return {"status": "error", "message": "request error"}

    return response.json()

@order_router.post("/scenario-camp2", response_model=Any)
async def scenario_camp2(
    iteration: int = Query(100, description="iteration", examples=100),
    delay_seconds: int = Query(5, description="delay seconds", examples=5),
):
    all_orders = []
    try:
        btc_balance, usdt_balance = 0, 0
        assets = (await balance())["balances"]
        for asset in assets:
            if asset["asset"] == "BTC":
                btc_balance = asset["free"]
            elif asset["asset"] == "USDT":
                usdt_balance = asset["free"]

        order_flag = "BUY"
        for _ in range(iteration):
            orderbook = await get_orderbook("BTCUSDT", 5)
            if order_flag == "BUY":
                # buy limit
                buy_price = float(orderbook["a"][0][0]) # second best ask price
                assets = (await balance())["balances"]
                for asset in assets:
                    if asset["asset"] == "USDT":
                        usdt_balance = asset["free"]
                        usdt_balance = math.floor(float(usdt_balance) * 100) / 100
                buy_quantity = math.floor(float(usdt_balance) / (float(buy_price) + 1000) * 100000) / 100000
                order = await buy_limit(symbol="BTCUSDT", price=buy_price, quantity=buy_quantity)
                logging.info(f"BUY: {str(buy_price)}$, {str(buy_quantity)}BTC -- {json.dumps(order)}")
                all_orders.append(order)
                time.sleep(random.uniform(delay_seconds, delay_seconds+2))
                order_flag = "SELL"
            elif order_flag == "SELL":
                # sell limit
                sell_price = float(orderbook["b"][-1][0])
                assets = (await balance())["balances"]
                for asset in assets:
                    if asset["asset"] == "BTC":
                        btc_balance = asset["free"]
                        btc_balance = math.floor(float(btc_balance) * 100000) / 100000
                sell_quantity = btc_balance
                order = await sell_limit(symbol="BTCUSDT", price=sell_price, quantity=sell_quantity)
                logging.info(f"SELL: {str(sell_price)}$, {str(sell_quantity)}BTC -- {json.dumps(order)}")
                all_orders.append(order)
                time.sleep(random.uniform(delay_seconds, delay_seconds+2))
                order_flag = "BUY"
            
            await cancel_orders_all()
            time.sleep(0.5)
    except Exception as e:
        print(e)
        return {"status": "error", "message": "request error"}
    
    return all_orders