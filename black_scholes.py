from math import exp, log, sqrt
from statistics import NormalDist

N = NormalDist().cdf

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
        
        return N(d1_) * und - N(d2_) * disc

    else:

        return N(-d2_) * disc - N(-d1_) * und