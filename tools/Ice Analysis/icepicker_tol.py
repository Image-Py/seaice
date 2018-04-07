import wx, osr
from imagepy.core.engine import Tool
from imagepy import IPy
import numpy as np
from imagepy.core.draw.fill import floodfill
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
        msk = floodfill(ips.img, x, y, 0, False)
        conts = find_contours(msk, 0.5, 'high')
        conts = conts[0][:,::-1]
        ips.mark = Mark(conts)
        

        trans = np.array(ips.info['trans']).reshape((2,3))
        jw = np.dot(trans[:,1:], conts.T).T+ trans[:,0]

        xian = 'PROJCS["Xian 1980 / Gauss-Kruger zone 17", GEOGCS["Xian 1980",DATUM["Xian_1980",SPHEROID["Xian  1980",6378140,298.257,AUTHORITY["EPSG","7049"]],AUTHORITY["EPSG","6610"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4610"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",120],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","2331"]]'

        osrprj = osr.SpatialReference()
        osrprj.ImportFromWkt(ips.info['proj'])
        osrgeo = osr.SpatialReference()
        osrgeo.ImportFromWkt(xian)
        ct = osr.CoordinateTransformation(osrprj, osrgeo)

        xy = ct.TransformPoints(jw)
        polygon = Polygon(xy)
        c = polygon.centroid
        IPy.set_info('At N:%.4f, E:%.4f  Area:%.4f'%(c.x, c.y, polygon.area))
        ips.update = True
        
    def mouse_up(self, ips, x, y, btn, **key):
        pass
    
    def mouse_move(self, ips, x, y, btn, **key):
        pass
        
    def mouse_wheel(self, ips, x, y, d, **key):
        pass
