from imagepy.core.engine import Tool
from imagepy import IPy
import numpy as np

class Plugin(Tool):
    title = 'Geo Coordinate'
        
    def mouse_down(self, ips, x, y, btn, **key):
        pass
    
    def mouse_up(self, ips, x, y, btn, **key):
        pass
    
    def mouse_move(self, ips, x, y, btn, **key):
        if not 'trans' in ips.info:
            return IPy.set_info('No Coordinate')
        trans = np.array(ips.info['trans']).reshape((2,3))
        jw = np.dot(trans[:,1:], (x, y))+ trans[:,0]
        IPy.set_info('X:%d Y:%d ==> N:%.4f, E:%.4f'%(x, y, jw[0], jw[1]))
        
    def mouse_wheel(self, ips, x, y, d, **key):
        pass
