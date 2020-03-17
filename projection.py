# -*- coding: utf-8 -*-
"""
FY-4A标称（NOM）全圆盘（DISK）数据的行列号经纬度互转
Created on 2018/11/08 21:25:32
@author: modabao
"""

from numpy import deg2rad, rad2deg, arctan, arcsin, tan, sqrt, cos, sin
import numpy as np
ea = 6378.137
eb = 6356.7523
h = 42164 
ooxxD = deg2rad(104.7)

COFF = {"0500M": 10991.5,
        "1000M": 5495.5,
        "2000M": 2747.5,
        "4000M": 1373.5}

CFAC = {"0500M": 81865099,
        "1000M": 40932549,
        "2000M": 20466274,
        "4000M": 10233137}
LOFF = COFF
LFAC = CFAC


def latlon2lc(lat, lon, resolution):
    lat = deg2rad(lat)
    lon = deg2rad(lon)
    eb2_ea2 = eb**2 / ea**2
    ooxxe = lon
    ooxx_e = arctan(eb2_ea2 * tan(lat))
    cosooxx_e = cos(ooxx_e)
    re = eb / sqrt(1 - (1 - eb2_ea2) * cosooxx_e**2)
    ooxxe_ooxxD = ooxxe - ooxxD
    r1 = h - re * cosooxx_e * cos(ooxxe_ooxxD)
    r2 = -re * cosooxx_e * sin(ooxxe_ooxxD)
    r3 = re * sin(ooxx_e)
    rn = sqrt(r1**2 + r2**2 + r3**2)
    x = rad2deg(arctan(-r2 / r1))
    y = rad2deg(arcsin(-r3 / rn))
    c = COFF[resolution] + x * 2**-16 * CFAC[resolution]
    l = LOFF[resolution] + y * 2**-16 * LFAC[resolution]
    return l, c


def lc2latlon(l, c, resolution):
    x = deg2rad((c - COFF[resolution]) / (2**-16 * CFAC[resolution]))
    y = deg2rad((l - LOFF[resolution]) / (2**-16 * LFAC[resolution]))
    cosx = cos(x)
    cosy = cos(y)
    siny = sin(y)
    cos2y = cosy**2
    hcosxcosy = h * cosx * cosy
    cos2y_ea_eb_siny_2 = cos2y + (ea / eb * siny)**2
    sd = sqrt(hcosxcosy**2 - cos2y_ea_eb_siny_2 * (h**2 - ea**2))
    sn = (hcosxcosy - sd) / cos2y_ea_eb_siny_2
    s1 = h - sn * cosx * cosy
    s2 = sn * sin(x) * cosy
    s3 = -sn * siny
    sxy = sqrt(s1**2 + s2**2)
    lon = rad2deg(arctan(s2 / s1) + ooxxD)
    lat = rad2deg(arctan(ea**2 / eb**2 * s3 / sxy))
    return lat, lon


if __name__ == "__main__":
    from numpy import arange, meshgrid, concatenate
    interp_steps = {"0500M": 0.005,
                   "1000M": 0.01,
                   "2000M": 0.02,
                   "4000M": 0.04}
    lat_low, lat_high = 0, 50
    lon_left, lon_right = 80, 130
    lat_low = int(1000 * lat_low)
    lat_high = int(1000 * lat_high)
    lon_left = int(1000 * lon_left)
    lon_right = int(1000 * lon_right)
    interp_steps = {x: int(y * 1000) for x, y in interp_steps.items()}
    lc = {}
    for resolution, interp_step in interp_steps.items():
        lat = arange(lat_high, lat_low-1, -interp_step) / 1000
        lon = arange(lon_left, lon_right+1, interp_step) / 1000
        lat = lat.astype(np.float32)
        lon = lon.astype(np.float32)
        lon, lat = meshgrid(lon, lat)
        l, c = latlon2lc(lat, lon, resolution)
        l = l[:, :, np.newaxis]
        c = c[:, :, np.newaxis]
        lc[resolution] = concatenate((l, c), axis=2)