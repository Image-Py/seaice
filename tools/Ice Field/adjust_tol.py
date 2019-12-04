import wx
import numpy as np
from numpy.linalg import norm, inv
from imagepy.core.engine import Tool, Filter,Simple
import scipy.ndimage as nimg
from imagepy.core.mark import GeometryMark
from geonumpy import GeoArray
from imagepy import IPy
        
class Plugin(Tool):
    title = 'Adjust'
    def __init__(self):
        self.curobj = None

    def pick(self, x, y, lst, lim):
        if len(lst)==0: return None
        ds = norm(np.array(lst)[:,:2] - (x, y), axis=1)
        return None if ds.min() > lim else lst[np.argmin(ds)]

    def update(self, ips):
        ips.mark = GeometryMark({'type':'layer', 'body':[
            {'type':'points', 'body':[(i[0], i[1]) for i in ips.data['adjc']]},
            {'type':'circles', 'body':[(i[0], i[1], i[2]) for i in ips.data['adjc']]},
            {'type':'texts', 'body':[(i[0], i[1], 'z=%.1f'%i[3]) for i in ips.data['adjc']]}]})
        ips.update()

    def mouse_down(self, ips, x, y, btn, **key):
        if not 'adjc' in ips.data: ips.data['adjc'] = []
        lim = 5.0/key['canvas'].scale
        if btn==1 and not key['ctrl']:
            self.curobj = self.pick(x, y, ips.data['adjc'], lim)
            if self.curobj!=None: return
            self.curobj = [x, y, 10, 5]
            ips.data['adjc'].append(self.curobj)
        if btn==1 and key['ctrl']:
            self.curobj = self.pick(x, y, ips.data['adjc'], lim)
            if self.curobj is None: return
            ips.data['adjc'].remove(self.curobj)
            self.curobj = None
        if btn==1 and key['alt']: del ips.data['adjc'][:]

        if btn==3:
            cur = self.pick(x, y, ips.data['adjc'], lim)
            if cur == None or not isinstance(ips.img, GeoArray): return
            trans = np.array(ips.img.mat)
            jw = np.dot(trans[:,1:], (cur[0], cur[1]))+ trans[:,0]
            para = {'e':jw[0], 'n':jw[1], 'r':cur[2], 'z':cur[3]}
            view = [(float, 'e', (0, 1e10), 6, 'E', ''),
                    (float, 'n', (0, 1e10), 6, 'N', ''),
                    (float, 'r', (5, 100), 0, 'R', ''),
                    (float, 'z', (0, 50), 1, 'Z', '')]
            rst = IPy.get_para('Setting', view, para)
            if rst:
                jw = para['e'], para['n']
                x, y = np.dot(inv(trans[:,1:]), jw-trans[:,0])
                cur[0], cur[1], cur[2], cur[3] = x, y, para['r'], para['z']
                self.update(ips)

        self.update(ips)
    
    def mouse_up(self, ips, x, y, btn, **key):
        self.curobj = None
    
    def mouse_move(self, ips, x, y, btn, **key):
        if 'trans' in ips.data:
            trans = np.array(ips.data['trans']).reshape((2,3))
            jw = np.dot(trans[:,1:], (x, y))+ trans[:,0]
            IPy.set_info('X:%d Y:%d ==> N:%.4f, E:%.4f'%(x, y, jw[0], jw[1]))

        if not 'adjc' in ips.data: return
        lim = 5.0/key['canvas'].scale
        if btn==None:
            self.cursor = wx.CURSOR_CROSS
            ison = self.pick(x, y, ips.data['adjc'], lim)
            if ison != None:
                self.cursor = wx.CURSOR_HAND
        elif btn==1:
            self.curobj[0], self.curobj[1] = x, y
            self.update(ips)
        
    def mouse_wheel(self, ips, x, y, d, **key):
        if not self.curobj is None:
            self.curobj[2] = max(5, self.curobj[2] + d)
            return self.update(ips)
        lim = 5.0/key['canvas'].scale
        ison = self.pick(x, y, ips.data['adjc'], lim)
        if not ison is None: 
            ison[3] = max(0, ison[3]+d*0.5)
            self.update(ips)