from black_scholes import price
from dash_core_components import Graph
from model import leg
from numpy import arange
import plotly.graph_objects as go
from typing import List

DPY = 365
PAYOFF_MIN = 0.5
PAYOFF_MAX = 2.0
STEPS = 2000

def price_leg(leg: leg, variables: dict):

    time = (leg.dte - variables["time"]) / DPY
    underlying_price = variables[leg.underlying.symbol]
    vol = variables[leg.id]["iv"]    
    rate = variables["rate"]

    res = 0

    if time > 0:
        
        res = price(
            call = leg.call,
            und = underlying_price,
            strike = leg.strike,
            time = time,
            vol = vol,
            rate = rate
        )

    else:

        if leg.call:

            res = max(0, underlying_price - leg.strike)

        else:

            res = max(0, leg.strike - underlying_price)
        
    return res * leg.quantity 


def get_payoffs(legs: List[leg], variables: dict, mode: str):

    front_leg = legs[0]
    nearest_underlying = front_leg.underlying

    min_ = nearest_underlying.price * PAYOFF_MIN
    max_ = nearest_underlying.price * PAYOFF_MAX
    inc = (max_ - min_) / STEPS

    x = arange(min_, max_, inc)
    y = []

    for x_ in x:

        y_ = 0
        variables[front_leg.underlying.symbol] = x_

        for leg in legs:

            y_ += price_leg(leg, variables) 
            if mode == "pnl": y_ -= leg.cost
        
        y.append(y_)

    return x, y


def get_payoff_graph(
    id: str, 
    legs: List[leg], 
    variables: dict,
    mode: str
) -> Graph:

    x, y = get_payoffs(legs, variables, mode)

    fig = go.Figure()

    fig.add_scatter(
        x = x,
        y = y,
        mode = "lines",
        name = "payoff"
    )

    # 0 line
    fig.add_hline(
        y = 0,
        line_color = "red",
        opacity = 0.2
    )

    # one line per strike
    for leg in legs:

        fig.add_vline(
            x = leg.strike,
            line_dash = "dot",
            line_color = "grey",
            opacity = 0.2
        )

    return Graph(
            id = id,
            figure = fig
        )