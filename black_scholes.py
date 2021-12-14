from math import exp, log, pow, sqrt
from statistics import NormalDist

cdf = NormalDist().cdf

def d1(
    und:    float,
    strike: float,
    time:   float,
    vol:    float,
    rate:   float
):

    return  1 / (vol * sqrt(time)) * \
            (log(und / strike) + (rate + vol**2 / 2) * time)


def d2(
    d1_:    float,
    time:   float,
    vol:    float
):

    return d1_ - vol * time


def price(
    call:   bool,
    und:    float,
    strike: float,
    time:   float,
    vol:    float,
    rate:   float
):

    d1_ = d1(und, strike, time, vol, rate)
    d2_ = d2(d1_, vol, time)
    disc = exp(-rate * time) * strike

    if call:
        
        return cdf(d1_) * und - cdf(d2_) * disc

    else:

        return cdf(-d2_) * disc - cdf(-d1_) * und