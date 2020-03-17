# -*- coding: utf-8 -*-
from osgeo import gdal, osr
import os
import numpy as np


class CreateFY4AFile():
    def __init__(self):
        pass

    def wirte(self, lat, lon, data, nodata, exportType, export_file):
        if 'int8' in data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in data.dtype.name:
            datatype = gdal.GDT_Int16
        elif 'float32' in data.dtype.name:
            datatype = gdal.GDT_Float32
        else:
            datatype = gdal.GDT_Float64
            
        driver = None
        if (exportType == "tif"):
            driver = gdal.GetDriverByName('GTiff')
            if (os.path.splitext(export_file)[-1] == ".tif"):
                pass
            else:
                print ("export_file name error")
                return
        if (exportType == "jpg"):
            driver = gdal.GetDriverByName('JPEG')
            if (os.path.splitext(export_file)[-1] == ".jpg"):
                pass
            else:
                print ("export_file name error")
                return
        elif (exportType == "img"):
            driver = gdal.GetDriverByName('HFA')
            if (os.path.splitext(export_file)[-1] == ".img"):
                pass
            else:
                print ("export_file name error")
                return
        elif (exportType == "grib2"):
            driver = gdal.GetDriverByName('GRIB')
            if (os.path.splitext(export_file)[-1] == ".GRB2"):
                pass
            else:
                print ("export_file name error")
                return
        driver.Register()
        if (nodata != None):
            nodata = np.asarray(nodata, dtype="double")
        if len(data.shape) == 3:
            im_bands, im_height, im_width = data.shape
        else:
            im_bands, (im_height, im_width) = 1, data.shape
        dataset = driver.Create(export_file, im_width, im_height, im_bands, datatype)
        local_transform = createGeotransform(lat, lon, order="asc")
        dataset.SetGeoTransform(local_transform)
        srs = createSrs("mercator")
        if (srs != None):
            dataset.SetProjection(srs)
        else:
            print ("input srs/proj error")  
            
        if im_bands == 1:
            dataset.GetRasterBand(1).WriteArray(data[0])  # 写入数组数据
            if (nodata != None and nodata.__len__() == 0):
                dataset.GetRasterBand(1).SetNoDataValue(nodata[0])  # 设置无效值
        else:
            for i in range(im_bands):
                dataset.GetRasterBand(i + 1).WriteArray(data[i])
                if (nodata != None):
                    if (nodata.__len__() != 0):
                        if (nodata[i] != None):
                            dataset.GetRasterBand(i+1).SetNoDataValue(nodata[i])  # 设置无效值
        del dataset


def createGeotransform(lat, lon, order):
    if (order == "asc"):
        local_transform = (
            min(lon), (max(lon) - min(lon)) / lon.__len__(), 0.0, max(lat), 0.0,
            (min(lat) - max(lat)) / lat.__len__())
    elif (order == "desc"): 
        local_transform = (
            min(lon), (max(lon) - min(lon)) / lon.__len__(), 0.0, min(lat), -0.0,
            abs((min(lat) - max(lat)) / lat.__len__()))
    return local_transform


def createXY(transform, xSize, ySize):
    lat = np.linspace(transform[5] * ySize + transform[3], transform[3], ySize)
    lon = np.linspace(transform[0], transform[1] * xSize + transform[0], xSize)
    lat = list(lat)
    lat.reverse()
    lat = np.asarray(lat)
    return (lat, lon)


def createSrs(projstr):
    if (projstr == "mercator"):
        srs4326 = osr.SpatialReference()
        srs4326.ImportFromEPSG(4326)
    proj = str(srs4326)
    return proj
