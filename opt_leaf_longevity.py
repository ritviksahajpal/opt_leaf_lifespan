#!/usr/bin/env python

"""
Optimise leaf lifespan given carbon gain and maintance and leaf construction
costs.

TODO:
- sensible cost numbers
- vary met data.

Reference:
---------
* Kikuzawa, K. 1991. A cost-benefit analysis of leaf habit and leaf longevity
  of trees and their geographical pattern. American Naturalist 138: 1250–1263.

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (06.09.2018)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
from scipy.optimize import minimize
from farquhar_mod import FarquharC3

import constants as c

def f(ndays, *args, **kws):
    # Optimise leaf lifespan

    (Ci, Tleaf, Par, Rd, Vcmax, Jmax, leaf_construction_cost) = args

    carbon_gain = calc_gain(ndays[0], Ci, Tleaf, Par, Rd, Vcmax, Jmax)

    A_day_avg = carbon_gain / ndays[0]
    maintence_cost = A_day_avg * 0.6 * ndays[0]
    g = (1.0 / ndays) * (carbon_gain - maintence_cost - leaf_construction_cost)

    return -1.0 * g

def calc_gain(ndays, Ci, Tleaf, Par, Rd, Vcmax, Jmax):

    daylight_hrs = 12
    days = np.arange(1, int(ndays))

    F = FarquharC3()

    carbon_gain = 0.0
    for i in days:
        A_day = 0.0
        for j in range(daylight_hrs*2):
            (An, Anc, Anj) = F.calc_photosynthesis(Ci=Ci, Tleaf=Tleaf, Par=Par,
                                                   Jmax=Jmax, Vcmax=Vcmax,
                                                   Rd=Rd)

            A_day += An * c.UMOL_TO_MOL * c.MOL_C_TO_GRAMS_C * c.SEC_TO_HLFHR
        carbon_gain += A_day

    return carbon_gain

deg2kelvin = 273.15
Tleaf = 25.0
Tleaf += deg2kelvin
Par = 1800.
Ca = 400.
Ci = Ca * 0.7
jv_ratio = 1.67
Vcmax = 50.0
Jmax = Vcmax * jv_ratio
Rd = Vcmax * 0.015

leaf_construction_cost = 100.0

leaf_construct_cost = np.linspace(100.0, 2000.0, 20)
gain_save = []
length = []
for lcost in leaf_construct_cost:
    # guess at growing season length
    x0 = [50]
    result = minimize(f, x0=x0, tol=1E-3,
                      args=(Ci, Tleaf, Par, Rd, Vcmax, Jmax, lcost),
                      bounds=[(1, 365*3)])
    days = result.x[0]

    carbon_gain = calc_gain(days, Ci, Tleaf, Par, Rd, Vcmax, Jmax)
    gain_save.append(carbon_gain / 365.)
    length.append(days)

plt.plot(leaf_construct_cost, length, "bo")
plt.xlabel("Leaf construction cost")
plt.ylabel("Leaf lifespan (d$^{-1}$)")
plt.show()