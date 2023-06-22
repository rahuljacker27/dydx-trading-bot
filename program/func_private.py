from datetime import datetime, timedelta
import time
from pprint import pprint
from func_utils import format_number

# Get existing open positions
def is_open_positions(client , market):

    #protect api
    time.sleep(0.2)

    #get positions
    all_positions = client.private.get_positions(
        market = market,
        status = "OPEN"
    )

    #Determine if open
    if len(all_positions.data["positions"]) > 0:
        return True
    else:
        return False


#check order status
def check_order_status(client, order_id):

    order = client.private.get_order_by_id(order_id)
    if order.data:
        if "order" in order.data["order"]["status"]:
            return order.data["order"]["status"]
    return "FAILED"



# Place market order
def place_market_order(client, market, side, size, price, reduce_only):
    # Get Position Id
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # Get expiration time
    server_time = client.public.get_time()
    # expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(minutes=1)
    # expiration_timestamp = int(expiration.timestamp())

    # Calculate the expiration time as 1 minute in the future from the current time
    # expiration = datetime.now() + timedelta(minutes=1)

    # # Convert the expiration time to a Unix timestamp
    # expiration_timestamp = int(expiration.timestamp())
    expiration = datetime.now() + timedelta(minutes=1.1)
    expiration_timestamp = int(expiration.timestamp())
    # Place an order
    placed_order = client.private.create_order(
        position_id=position_id, # required for creating the order signature
        market=market,
        side=side,
        order_type="MARKET",
        post_only=False,
        size=size,
        price=price,
        limit_fee='0.015',
        expiration_epoch_seconds = expiration_timestamp,
        time_in_force="FOK",
        reduce_only=reduce_only
    )

    return placed_order.data

# Abort all open positions 
def abort_all_positions(client):

    # cancel all orders
    client.private.cancel_all_orders()

    #protect API
    time.sleep(0.5)

    # Get markets for reference of tick size
    markets = client.public.get_markets().data
    # pprint(markets)

    #protect API
    time.sleep(0.5)

    #Get all open positions
    positions = client.private.get_positions(status="OPEN")
    all_positions = positions.data["positions"]

    # pprint(all_positions)

    #Handle open positions
    close_order = []
    if len(all_positions) > 0:

        #loop through each position
        for position in all_positions:

            #Determine Market
            market = position["market"]

            #Determine Side
            side = "BUY"
            if position["side"] == "LONG":
                side = "SELL"
            
            # print(market, side)
            
            #Get price
            price = float(position["entryPrice"])
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)

            # Place order to close
            order = place_market_order(
                client,
                market,
                side,
                position["sumOpen"],
                accept_price,
                True
            )

            #Apeend the results
            close_order.append(order)

            #protect API
            time.sleep(0.5)
        return close_order
