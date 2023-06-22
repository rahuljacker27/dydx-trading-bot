from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx
from func_private import abort_all_positions
from func_public import construct_market_prices
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions
from func_exit_pairs import manage_trade_exits


if __name__ == "__main__":

    #connect to client
    try:
        print("Connecting to client...")
        client = connect_dydx()
    except Exception as e:
        print(e)
        print("Error connecting to client : ", e)
        exit(1)

    # Abort all open positions
    if ABORT_ALL_POSITIONS:
        try:
            print("CLosing all positions...")
            close_orders = abort_all_positions(client)
        except Exception as e:
            print("Error closing all positions : ", e)
            exit(1)

    #Find cointegrated Pairs
    if FIND_COINTEGRATED:

        #construct market prices
        try:
            print("Fetching market prices , please allow 3 mins...")
            df_market_price = construct_market_prices(client)
        except Exception as e:
            print("Error contructing market prices : ", e)
            exit(1)

        #store cointegrated pairs
        try:
            print("Storing Cointegrated pairs...")
            stores_result = store_cointegration_results(df_market_price)
            if stores_result != "saved":
                print("Error saving cointegrated pairs")
                exit(1)
        except Exception as e:
            print("Error saving cointegrated pairs : ", e)
            exit(1)

    while True:

        # Place Trades for opening positions
        if MANAGE_EXITS:
            try:
                print("Managing exits ...")
                manage_trade_exits(client)
            except Exception as e:
                print("Error Trading pairs : ", e)
                exit(1)


        # Place Trades for opening positions
        if PLACE_TRADES:
            try:
                print("Finding trading opportunities...")
                open_positions(client)
            except Exception as e:
                print("Error Trading pairs : ", e)
                exit(1)