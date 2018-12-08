from imagepy import IPy
import numpy as np
from imagepy.core.engine import Simple, Filter,Tool,Table
from imagepy.core.manager import ImageManager,TableManager
from imagepy.core.mark import GeometryMark
from imagepy.core import ImagePlus
# import pandas as pd
import gdal
import wx
from skimage.draw import polygon 
from scipy.stats import linregress
import pandas as pd
import matplotlib.pyplot as plt
def pix2jw(trans,point):
    point=np.array(point)
    return np.dot(trans[:,1:], point.T).T+ trans[:,0]
def jw2pix(trans,jw):
    #求出逆矩阵
    inv=np.linalg.inv(trans[:,1:])
    point=np.dot(jw-trans[:,0],inv)
    return point
# def build_grid(jw1,jw2,interval):
#     x, y = np.meshgrid(np.arange(min(jw1[0],jw2[0]),max(jw1[0],jw2[0]),interval[0]), np.arange(min(jw1[1],jw2[1]),max(jw1[1],jw2[1]),interval[1]))
#     grid_shape=y.shape
#     x, y = x.flatten(), y.flatten()
#     points = np.vstack((x,y)).T
#     points=points.reshape((grid_shape[0],grid_shape[1],2))
#     return points
def build_grid(jw1,jw2,interval):
    x, y = np.meshgrid(np.arange(min(jw1),max(jw1),interval[0]), np.arange(min(jw2),max(jw2),interval[1]))
    shape=x.shape
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x,y)).T
    return points,shape
def jw2polygon(trans,jw_data,interval):
    polygon_data=np.array([np.vstack((i,i,i,i))+np.array([[0,0],[0,interval[1]],interval,[interval[0],0]]) for i in jw_data])
    return polygon_data
def get_mask(img,polygon_data):
    shape=img.shape
    msk=np.zeros(shape)
    r = polygon_data[:,1]
    c = polygon_data[:,0]
    rr, cc = polygon(r, c)
    msk[rr, cc] = 1
    return msk.astype('uint8')
def get_gray(img,polygon_data):
    msk=get_mask(img,polygon_data)
    img*=msk
    gray=img[img>0].mean()
    return gray
# class Statistic(Table):
#     title = 'Table Statistic'
#     para = {'map1':None}
        
#     view = [('tab',  'map1', 'map', '')]

#     def run(self, tps, data, snap, para=None):
#         # print('map_title',self.para['map1'])
#         # print('data',help(TableManager.get(self.para['map1']).data))
#         map=TableManager.get(self.para['map1']).data.values[1,:]
#         print('data',map)
#         # print('numpy',TableManager.get(self.para['map1']).data.values)
#         # print('data',TableManager.get(self.para['map1']).data[0])
class DrawGrid(Simple):
    title = 'Draw Grid'
    note = ['8-bit', 'preview']
    view = [(float, 'longtitude_max', (-180,180), 8, 'longtitude_max', 'degree'),
            (float, 'longtitude_min', (-180,180), 8, 'longtitude_min', 'degree'),
            (float, 'latitude_max',(-90,90), 8, 'latitude_max', 'degree'),            
            (float, 'latitude_min',(-90,90), 8, 'latitude_min', 'degree'),
            (float, 'latitude_inter',(0,100), 3, 'latitude_inter', 'degree'),
            (float, 'longtitude_inter',(0,100), 3, 'longtitude_inter', 'degree'),
            ('tab',  'map1', 'map', ''),
            ]
            # (float, 'e', (-100,100), 1, 'eccentricity', 'ratio')
    para = {'longtitude_max':122.34921875, 'longtitude_min':120.10546875,'latitude_max':40.98600002,'latitude_min':39.73600008,
    'latitude_inter':0.100,'longtitude_inter':0.100,'map1':None}
    # def load(self, ips):pass
    def preview(self, ips, para):
        print('preview')
        self.draw_grid(ips)
    def run(self, ips, imgs=None, para = None):
        gray_data=self.draw_grid(ips)
        map=TableManager.get(self.para['map1']).data.values[1,:]
        thick=map[gray_data.astype(int)]
        IPy.show_table(pd.DataFrame(thick),title='thick')
    def draw_grid(self,ips):
        print('data',ips.data)
        trans = np.array(ips.info['trans']).reshape((2,3))
        jw1,jw2=(self.para['longtitude_min'],self.para['longtitude_max']),(self.para['latitude_min'],self.para['latitude_max'])
        interval=(self.para['latitude_inter'],self.para['longtitude_inter'])
        jw_data,shape=build_grid(jw1,jw2,interval)
        polygon_data=jw2pix(trans,jw2polygon(trans,jw_data,interval))
        # ips.data=polygon_data
        gray_data=np.array([get_gray(ips.imgs[0].copy(),i) for i in polygon_data]).reshape(shape)[::-1,:]
        print('shape',gray_data.shape)

        mark =  {'type':'layers', 'body':{}}
        layer = {'type':'layer', 'body':[]}

        texts_xy=(polygon_data[:,0,:]+polygon_data[:,2,:])/2
        ips.test_id={'type':'texts', 'body':[(i[0][0],i[0][1],str(i[1])) for i in zip(texts_xy.tolist(),np.arange(len(texts_xy)))]}

        layer['body']=[{'type':'polygons', 'body':polygon_data},ips.test_id]
        # layer['body']=[{'type':'polygons', 'body':polygon_data}]
        mark['body'][0] = layer
        ips.mark=GeometryMark(mark)
        ips.update = True
        return gray_data
plgs = [DrawGrid]