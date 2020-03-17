# -*- coding: utf-8 -*-
from h5py import File as h5File
import numpy as np
from projection import latlon2lc
from numpy import rint

CONTENTS = {"0500M": ("Channel02",),
            "1000M": ("Channel01", "Channel02", "Channel03"),
            "2000M": tuple(["Channel{x:02d}" for x in range(1, 7)]),
            "4000M": tuple(["Channel{x:02d}" for x in range(1, 15)])}

SIZES = {"0500M": 21984,
         "1000M": 10992,
         "2000M": 5496,
         "4000M": 2748}


class FY4A_H5(object):
    def __init__(self, hdf5File, channelnames=None):
        self.h5file = h5File(hdf5File, 'r')
        self.channelnames = channelnames or CONTENTS[hdf5File[-15:-10]]
        self.channels = {x: None for x in self.channelnames}
        self.channelsValues = []
        self.geo_range = None
        self.l = None
        self.c = None
        self.l_begin = self.h5file.attrs["Begin Line Number"]
        self.l_end = self.h5file.attrs["End Line Number"]

    def __del__(self):
        self.h5file.close()

    def extract(self, channelnames, geo_range=None, resolution=None):
        for channelname in channelnames:
            NOMChannelname = "NOM" + channelname
            CALChannelname = "CAL" + channelname
            if geo_range is None:
                channel = self.h5file[NOMChannelname].value
                self.channels[channelname] = channel
                return None
            geo_range_final = eval(geo_range)
            if self.geo_range != geo_range_final:
                self.geo_range = geo_range_final
                lat_S, lat_N, lon_W, lon_E, step = geo_range_final
                lat = np.arange(lat_N, lat_S - 0.005, -step)
                lon = np.arange(lon_W, lon_E + 0.005, step)
                lon, lat = np.meshgrid(lon, lat)
                if (resolution is None):
                    return None
                self.l, self.c = latlon2lc(lat, lon, resolution)
                self.l = rint(self.l).astype(np.uint16)
                self.c = rint(self.c).astype(np.uint16)
            channel = self.h5file[NOMChannelname].value[self.l - self.l_begin, self.c]
            channel[channel > 60000] = 4095
            #channel[channel == 65533] = 4095
            #channel[channel == 65534] = 4095
            #channel[channel == 65535] = 4095
            CALChannel = self.h5file[CALChannelname].value
            self.channelsValues.append(CALChannel[channel])
        self.channelsValues = np.asarray(self.channelsValues)
