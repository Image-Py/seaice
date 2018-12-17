from imagepy import IPy
import numpy as np
from imagepy.core.engine import Simple, Filter,Tool,Table
from imagepy.core.manager import ImageManager,TableManager
from imagepy.core.mark import GeometryMark
from imagepy.core import ImagePlus
import gdal
import wx
from skimage.draw import polygon 
from scipy.stats import linregress
import pandas as pd
import matplotlib.pyplot as plt

class GridValue(Simple):
    title = 'Grid Value'
    note = ['8-bit', 'preview']
    view = [(float, 'longtitude_max', (-180,180), 8, 'longtitude_max', 'degree'),
            (float, 'longtitude_min', (-180,180), 8, 'longtitude_min', 'degree'),
            (float, 'latitude_max',(-90,90), 8, 'latitude_max', 'degree'),            
            (float, 'latitude_min',(-90,90), 8, 'latitude_min', 'degree'),
            (float, 'latitude_inter',(0,100), 3, 'latitude_inter', 'degree'),
            (float, 'longtitude_inter',(0,100), 3, 'longtitude_inter', 'degree')]
            # (float, 'e', (-100,100), 1, 'eccentricity', 'ratio')
    para = {'longtitude_max':124.5, 'longtitude_min':117.5,'latitude_max':40,
        'latitude_min':37, 'latitude_inter':0.100,'longtitude_inter':0.100}
    # def load(self, ips):pass

    def grid(slef, ips, para):
        lons = np.arange(para['longtitude_min'], para['longtitude_max'], para['longtitude_inter'])
        lats = np.arange(para['latitude_min'], para['latitude_max'], para['latitude_inter'])
        trans = np.array(ips.info['trans']).reshape((2,3))
        lines = []
        jw2pix = lambda trans, i : np.dot(i-trans[:,0], np.linalg.inv(trans[:,1:]))
        for r in range(len(lats)-1):
            line = []
            for c in range(len(lons)-1):
                p1, p2 = (lons[c],lats[r]),(lons[c],lats[r+1])
                p3, p4 = (lons[c+1],lats[r+1]),(lons[c+1],lats[r])
                rect = [jw2pix(trans, i) for i in [p1, p2, p3, p4]]
                line.append([tuple(i) for i in rect])
            lines.append(line)
        return lines

    def preview(self, ips, para):
        lines = self.grid(ips, para)
        polygon_data = []
        for i in lines: polygon_data.extend(i)
        polygons = {'type':'polygons', 'body':polygon_data}
        ips.mark = GeometryMark(polygons)
        ips.update = True

        
    def run(self, ips, imgs=None, para = None):
        lines = self.grid(ips, para)
        mjd = []
        for line in lines:
            for pts in line:
                msk = polygon(* np.array(pts).T[::-1], shape=imgs[0].shape[:2])
                mjd.append(ips.img[msk[0], msk[1]].mean())
        data = np.array(mjd).reshape((len(lines), len(lines[0])))
        IPy.show_table(pd.DataFrame(data), title=ips.title+'-mjd')

plgs = [GridValue]