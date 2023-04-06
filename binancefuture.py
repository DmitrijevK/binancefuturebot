import time
from binance.client import Client

def connect_to_binance_future(api_key, api_secret):
    """Connects to Binance Futures API and returns a Client object."""
    client = Client(api_key=api_key, api_secret=api_secret)
    futures_client = client.futures_api()
    return futures_client

# Define the initial position size and stop loss percentage
position_sizes = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
stop_loss_percentages = [0.03, 0.04, 0.05, 0.06, 0.07]

# Define the leverage for the position
leverage = 20

# Define the achievement grid profit for setting a trailing stop order
PNL_LIST = [0.07, 0.1, 0.15, 0.2, 0.25]

# Define the number of consecutive stop losses before resetting the loss counter and position size
n = 10

# Define the initial loss counter
loss_counter = 0

# Define the initial position size
position_size = sum(position_sizes)

# Define the initial stop loss percentage
stop_loss_percentage = stop_loss_percentages[0]

# Define the initial trailing stop order price
trailing_stop_order_price = None

# Define the initial direction of the position
position_direction = "BUY"

# Define the initial entry price of the position
entry_price = None

# Define the initial profit of the position
profit = None

# Define the initial stop loss order id
stop_loss_order_id = None

# Define the initial trailing stop order id
trailing_stop_order_id = None

def place_trailing_stop_order(client, side, position_size, SYMBOL, entry_price, pnl, pnl_achieved, stop_loss):
    """Place a trailing stop order with the given parameters"""
    stop_price = entry_price - (entry_price * stop_loss)
    tp_price = entry_price + ((entry_price * pnl) * pnl_achieved)
    if side == "BUY":
        trailing_stop_price = tp_price if tp_price > stop_price else stop_price
    else:
        trailing_stop_price = tp_price if tp_price < stop_price else stop_price
    trailing_order = client.futures_create_order(
        symbol=SYMBOL,
        side="BUY" if side == "SELL" else "SELL",
        type="TRAILING_STOP_MARKET",
        quantity=position_size,
        stopPrice=trailing_stop_price,
        workingType="CONTRACT_PRICE",
        reduceOnly=True
    )
    return trailing_order

def handle_position(client, position, current_price, SYMBOL, position_size, stop_loss_percentage, trailing_stop_order_price, loss_counter, position_direction, entry_price, profit, stop_loss_order_id, trailing_stop_order_id):
    """Handle a position with the given current price."""

    # Calculate the current value of the position
    current_value = position['positionAmt'] * current_price

    # Check if the position is profitable or not
    if current_value > position['entryPrice'] * position['positionAmt']:
        # Calculate the profit
        profit = current_value - position['entryPrice'] * position['positionAmt']
        print(f"The position is profitable! Profit: ${profit:.2f}")

        target_profit = profit * 0.9 # Set target profit to 90% of the actual profit
    if profit >= target_profit:
        print("Target profit reached. Closing the position.")
        # Create a market order to close the position
        order = client.futures_create_order(
            symbol=SYMBOL,
            side="SELL" if position['positionAmt'] > 0 else "BUY",
            type="MARKET",
            quantity=abs(position['positionAmt'])
        )
        print(f"Market order to close the position created. Order ID: {order['orderId']}")
        return 'close'

    # Check if the profit is equal to or greater than the average of the stop loss and trailing stop prices
    if trailing_stop_order_price is not None and stop_loss_order_id is not None and trailing_stop_order_id is not None:
        stop_loss_order = client.futures_get_order(symbol=SYMBOL, orderId=stop_loss_order_id)
        trailing_stop_order = client.futures_get_order(symbol=SYMBOL, orderId=trailing_stop_order_id)
        if stop_loss_order['status'] == 'FILLED' and trailing_stop_order['status'] == 'FILLED':
            stop_loss_price = stop_loss_order['avgPrice']
            trailing_stop_price = trailing_stop_order['avgPrice']
            avg_price = (stop_loss_price + trailing_stop_price) / 2
            pnl = (current_price - avg_price) / avg_price
            if pnl >= 0.01: # Set pnl to 1%
                print("Target profit reached. Shifting the stop loss.")
                stop_loss_percentage = (stop_loss_percentage + trailing_stop_order_price) / 2
                trailing_stop_order_price = None
                loss_counter = 0
                position_direction = "BUY" if position_direction == "SELL" else "SELL"
                entry_price = current_price
                position_size = sum(position_sizes)
                # Create a stop loss order with the given parameters
                stop_loss_order = client.futures_create_order(
                    symbol=SYMBOL,
                    side="SELL" if position_direction == "BUY" else "BUY",
                    type="STOP_MARKET",
                    quantity=position_size,
                    stopPrice=entry_price * (1 - stop_loss_percentage),
                    workingType="CONTRACT_PRICE",
                    reduceOnly=True
                )
                print(f"Stop loss order created. Order ID: {stop_loss_order['orderId']}")
                stop_loss_order_id = stop_loss_order['orderId']

    # Check if the loss counter is greater than or equal to the maximum number of consecutive stop losses
    if loss_counter >= n:
        print(f"{n} consecutive stop losses reached. Resetting position size and loss counter.")
        loss_counter = 0
        position_size = sum(position_sizes)
        stop_loss_percentage = stop_loss_percentages[0]

    # Check if the current price is equal to or lower than the stop loss price
    if current_price <= entry_price * (1 - stop_loss_percentage):
        print("Stop loss hit. Closing the position.")
        # Create a market order to close the position
        order = client.futures_create_order(
            symbol=SYMBOL,
            side="SELL" if position['positionAmt'] > 0 else "BUY",
            type="MARKET",
            quantity=abs(position['positionAmt'])
        )
        print(f"Market order to close the position created. Order ID: {order['orderId']}")
        loss_counter += 1
        position_size = position_sizes[loss_counter]
        stop_loss_percentage = stop_loss_percentages[0]
        return 'close'

   
