def simple_moving_average_strat(df, window_fast, window_slow):
    df["sma_fast"] = df['close'].rolling(window=window_fast).mean()
    df["sma_slow"] = df['close'].rolling(window=window_slow).mean()

    if df["sma_fast"].iloc[-1] > df["sma_slow"].iloc[-1]:
        return "buy"
    elif df["sma_fast"].iloc[-1] < df["sma_slow"].iloc[-1]:
        return "sell"
    else:
        return "hold"

def place_order(signal, symbol, qty, api):
    if signal == "buy":
        api.submit_order(symbol=symbol, qty=qty, side="buy", type='market', time_in_force='gtc')
    if signal == "sell":
        api.submit_order(symbol=symbol, qty=qty, side="sell", type='market', time_in_force='gtc')