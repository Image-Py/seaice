from imagepy import IPy
import numpy as np
from imagepy.core.engine import Simple, Filter,Tool
from imagepy.core.manager import ImageManager
from imagepy.core.mark import GeometryMark
from imagepy.core import ImagePlus
import pandas as pd
import gdal
import wx
from skimage.draw import polygon 
from scipy.stats import linregress
import pandas as pd
def pix2jw(trans,point):
    point=np.array(point)
    return np.dot(trans[:,1:], point.T).T+ trans[:,0]
def jw2pix(trans,jw):
    #求出逆矩阵
    inv=np.linalg.inv(trans[:,1:])
    point=np.dot(jw-trans[:,0],inv)
    return point
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
class NewTool(Simple):
    para = {'thickness':0}
    view = [(float, 'thickness', (0,1000), 3, 'thickness', 'pix'),]
    title = 'para'
    note = [ 'all', 'preview']
    def load(self, ips=None):
        print('load')
        if str(self.index) in self.parent.thick.keys():
            self.para['thickness']=self.parent.thick[str(self.index)][1]
        else:self.para['thickness']=0
        return True
    def preview(self, ips, para):
        self.ok(self.ips)
    def run(self, parent, doc, para):
        self.parent.thick[str(self.index)]=[self.ips.gray_data[self.index],self.para['thickness']]
class Setting(Tool):
    title = 'set point'
    thick={}
    def mouse_down(self, ips, x, y, btn,  **key):
        print(x,y)
        if key['ctrl']:
            slope,intercept=self.lineregress(self.thick)
            print(slope,ips.gray_data,intercept)
            # thick_out=ips.gray_data*slope+intercept
            thick_out=ips.gray_data*np.array(slope)+np.array(intercept)
            thick_out=thick_out.reshape(ips.grid_shape)[::-1,:]
            # print(thick_out.reshape(ips.grid_shape))
            IPy.show_table(pd.DataFrame(thick_out),title='temp')
            return 
        index,i=self.pick(ips, x, y, btn)
        if index:
            # print(x,y,i)
            pd1 = NewTool()
            pd1.parent,pd1.index=self,i
            pd1.ips=ips
            pd1.start()  
        else:print(self.thick)
    def pick(self, ips, x, y, btn, **key):
        lim=3
        for i in range(len(ips.test_id['body'])):
            ox,oy=ips.test_id['body'][i][0],ips.test_id['body'][i][1]
            if abs(x-ox)<lim and abs(y-oy)<lim:return(True,i)
        return (False,-1)
    def mouse_move(self, ips, x, y, btn, **key):
        index,i=self.pick(ips, x, y, btn)
        if index==True:
            self.cursor = wx.CURSOR_HAND
            if str(i) in self.thick.keys():
                IPy.set_info('Gray:'+str(round(ips.gray_data[i],2))+',Thick:'+str(self.thick[str(i)]))
            else:IPy.set_info('Gray:'+str(round(ips.gray_data[i],2))+',Thick:0')
        else:self.cursor = wx.CURSOR_CROSS
    def mouse_wheel(self, ips, x, y, d, **key):
        pass
    def lineregress(self,thick):
        data=np.array(list(thick.values()))
        print(thick)
        print(data)
        print(data[:,0],data[:,1])
        slope, intercept, r_value, p_value, std_err = linregress(data[:,0], data[:,1])
        return slope,intercept
class DrawGrid(Simple):
    title = 'Draw Grid'
    note = ['8-bit']
    view = [(float, 'longtitude_max', (-180,180), 8, 'longtitude_max', 'degree'),
            (float, 'longtitude_min', (-180,180), 8, 'longtitude_min', 'degree'),
            (float, 'latitude_max',(-90,90), 8, 'latitude_max', 'degree'),            
            (float, 'latitude_min',(-90,90), 8, 'latitude_min', 'degree'),
            (float, 'latitude_inter',(0,100), 3, 'latitude_inter', 'degree'),
            (float, 'longtitude_inter',(0,100), 3, 'longtitude_inter', 'degree'),
            ]
            # (float, 'e', (-100,100), 1, 'eccentricity', 'ratio')
    para = {'longtitude_max':122.34921875, 'longtitude_min':120.10546875,'latitude_max':40.98600002,'latitude_min':39.73600008,
    'latitude_inter':0.100,'longtitude_inter':0.100}
    # def load(self, ips):pass
    def run(self, ips, imgs, para = None):
        trans = np.array(ips.info['trans']).reshape((2,3))

        jw1,jw2=(self.para['longtitude_min'],self.para['longtitude_max']),(self.para['latitude_min'],self.para['latitude_max'])
        interval=(self.para['latitude_inter'],self.para['longtitude_inter'])
        # print(jw1,jw2)
        jw_data,ips.grid_shape=build_grid(jw1,jw2,interval)
        polygon_data=jw2pix(trans,jw2polygon(trans,jw_data,interval))
        ips.data=polygon_data
        ips.gray_data=[get_gray(ips.imgs[0].copy(),i) for i in polygon_data]

        mark =  {'type':'layers', 'body':{}}
        layer = {'type':'layer', 'body':[]}

        texts_xy=(polygon_data[:,0,:]+polygon_data[:,2,:])/2
        ips.test_id={'type':'texts', 'body':[(i[0][0],i[0][1],str(i[1])) for i in zip(texts_xy.tolist(),np.arange(len(texts_xy)))]}

        layer['body']=[{'type':'polygons', 'body':polygon_data},ips.test_id]
        mark['body'][0] = layer
        ips.mark=GeometryMark(mark)
        ips.update = True

plgs = [DrawGrid,Setting]