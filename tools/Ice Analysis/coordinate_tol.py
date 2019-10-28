from imagepy.core.engine import Tool
from geonumpy import GeoArray
from imagepy import IPy
import numpy as np

class Plugin(Tool):
    title = 'Geo Coordinate'
        
    def mouse_down(self, ips, x, y, btn, **key):
        pass
    
    def mouse_up(self, ips, x, y, btn, **key):
        pass
    
    def mouse_move(self, ips, x, y, btn, **key):
        if not isinstance(ips.img, GeoArray):
            return IPy.set_info('No Coordinate')
        trans = ips.img.mat
        jw = np.dot(ips.img.mat[:,1:], (x, y))+ ips.img.mat[:,0]
        IPy.set_info('X:%d Y:%d ==> N:%.4f, E:%.4f'%(x, y, jw[0], jw[1]))
        
    def mouse_wheel(self, ips, x, y, d, **key):
        pass
