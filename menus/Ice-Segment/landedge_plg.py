from imagepy.core.engine import Simple
from imagepy.core.roi import PolygonRoi, roiio, convert
from shapely.affinity import affine_transform
from imagepy.core.manager import RoiManager
import geopandas as gpd
import geonumpy as gnp
from osgeo import osr
from imagepy import IPy
from os import path as osp
from numpy.linalg import inv
import numpy as np

class Open(Simple):
    title = 'Open Geo Roi'
    note = ['all']
    para = {'path':''}

    def check(self, ips):
        if not Simple.check(self, ips): return False
        if not isinstance(ips.img, gnp.GeoArray):
            IPy.alert('No geotransform found!')
        else: return True

    def show(self):
        filt = '|'.join(['%s files (*.%s)|*.%s'%(i.upper(),i,i) for i in ['shp']])
        return IPy.getpath('Save..', filt, 'open', self.para)

    #process
    def run(self, ips, imgs, para = None):
        gdf = gpd.read_file(para['path']).to_crs(ips.img.crs)
        m = ips.img.mat
        m = [1/m[0,1], 0, 0, 1/m[1,2], -m[0,0]/m[0,1], -m[1,0]/m[1,2]]
        shp = affine_transform(gdf['geometry'][0], m)
        ips.roi = convert.shape2roi(shp)
        if 'back' in ips.data:ips.roi.fill(ips.data['back'], (0,0,80))

class Save(Simple):
    title = 'Save Geo Roi'
    note = ['all', 'req_roi']
    para={'path':''}

    def check(self, ips):
        if not Simple.check(self, ips): return False
        if not isinstance(ips.img, gnp.GeoArray):
            IPy.alert('No geotransform found!')
        else: return True

    def show(self):
        filt = '|'.join(['%s files (*.%s)|*.%s'%(i.upper(),i,i) for i in ['shp']])
        return IPy.getpath('Save..', filt, 'save', self.para)

    def run(self, ips, imgs, para = None):
        shp = convert.roi2shape(ips.roi)
        m = ips.img.mat
        m = [m[0,1], 0, 0, m[1,2], m[0,0], m[1,0]]
        shp = affine_transform(shp, m)
        shp = affine_transform(shp, [0,1,1,0,0,0])
        gdf = gpd.GeoDataFrame([[shp]], columns=['geometry'], crs=ips.img.crs)
        gdf.to_file(para['path'])        

plgs = [Open, Save]