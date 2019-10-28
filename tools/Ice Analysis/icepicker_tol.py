import wx, osr
from imagepy.core.engine import Tool
from imagepy import IPy
import numpy as np
from skimage.morphology import flood_fill, flood
from skimage.measure import find_contours
from imagepy.core.roi.convert import shape2roi, roi2shape
from shapely.geometry import Polygon, Point

class Mark:
    def __init__(self, body):
        self.body = body
        
    def draw(self, dc, f, **key):
        dc.SetPen(wx.Pen((255,0,0), width=1, style=wx.SOLID))
        dc.DrawLines([f(*i) for i in self.body])

class Plugin(Tool):
    title = 'Ice Picker'
            
    def mouse_down(self, ips, x, y, btn, **key): 
        if btn!=1: return
        msk = flood(ips.img, (int(y), int(x)), connectivity=0, tolerance=0)
        conts = find_contours(msk, 0.5, 'high')
        conts = conts[0][:,::-1]
        ips.mark = Mark(conts)
        

        trans = ips.img.mat
        jw = np.dot(trans[:,1:], conts.T).T+ trans[:,0]

        osrprj = osr.SpatialReference()
        osrprj.ImportFromWkt(ips.img.crs)
        osrgeo = osr.SpatialReference()
        osrgeo.ImportFromEPSG(3857)
        ct = osr.CoordinateTransformation(osrprj, osrgeo)

        xy = ct.TransformPoints(jw)
        polygon = Polygon(xy)
        c = polygon.centroid
        IPy.set_info('At N:%.4f, E:%.4f  Area:%.4f'%(c.x, c.y, polygon.area))
        ips.update()
        
    def mouse_up(self, ips, x, y, btn, **key):
        pass
    
    def mouse_move(self, ips, x, y, btn, **key):
        pass
        
    def mouse_wheel(self, ips, x, y, d, **key):
        pass
