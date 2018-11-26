import wx
import numpy as np
from imagepy.core.engine import Tool, Filter,Simple
import scipy.ndimage as nimg
from imagepy.core.mark import GeometryMark
from .circle import Circle

from imagepy import IPy
from imagepy.core import ImagePlus
from scipy import interpolate
from imagepy.core import myvi

class Plugin(Circle):
    title = 'adjust'
    note = ['8-bit', 'auto_snap']
    fac_state=0
    def change_view(self,ips):
        print(self.body[0]['body'],self.body[1]['z'])
        # img_ori=ips.imgs[0].copy()
        #在第一次滑动滑轮时时候进行因子层刷新
        print('state',self.fac_state)
        if self.fac_state==0:
            ips.data=self.bulid_data(ips.imgs[0].shape,np.array([self.body[1]['body'],self.body[1]['z']]))
            ips.temp1=ips.imgs[0].copy()
            ips.imgs[0][:]=ips.data.copy()
            self.fac_state=1
        elif self.fac_state==1:
            ips.imgs[0][:]=ips.data*ips.temp1
            self.fac_state=2
        elif self.fac_state==2:
            ips.imgs[0][:]=ips.temp1.copy()
            self.fac_state=0
        ips.update = 'pix'
    def bulid_data(self,shape,data):
        z=data[1].astype(np.float64)
        data=np.array([list(i) for i in data[0]])
        x,y,weight=data[:,1],data[:,0],data[:,2]
        tck = interpolate.bisplrep(x, y, z, w=weight,kx=2,ky=2)
        znew = interpolate.bisplev(np.arange(shape[0]),np.arange(shape[1]), tck)
        return znew.astype(int)