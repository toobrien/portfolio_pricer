from math import exp, log, sqrt
from statistics import NormalDist

cdf = NormalDist().cdf

def price(
    call:   bool,
    und:    float,
    strike: float,
    time:   float,
    vol:    float,
    rate:   float
) -> float:

    d1_ =   1 / (vol * sqrt(time)) * \
            (log(und / strike) + (rate + vol**2 / 2) * time)
    
    d2_ =   d1_ - vol * sqrt(time)

    disc =  exp(-rate * time) * strike

    if call:
        
        return cdf(d1_) * und - cdf(d2_) * disc

    else:

        return cdf(-d2_) * disc - cdf(-d1_) * und