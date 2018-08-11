from imagepy import IPy
from imagepy.core import ImagePlus
import wx
import numpy as np
from imagepy.core.engine import Simple, Free
from imagepy.core.manager import WindowsManager
from scipy.ndimage import label, generate_binary_structure
from skimage.measure import regionprops
from shapely.geometry import Polygon, Point
from skimage.measure import find_contours
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import matplotlib.font_manager as fm
from wx.lib.pubsub import pub
import osr, gdal, ogr
import pandas as pd

def showicehist(areas):
    plt.figure('Ice Histogram')
    ax = plt.gca()
    n, bins, patches = ax.hist(areas, 50)
    ax.set_xlabel('Area (m^2)')
    ax.set_ylabel('Frequence')
    ax.set_title('Ice Area Histogram')
    plt.show()

pub.subscribe(showicehist, 'showicehist')

# center, area, l, extent, cov
class IceStatic(Simple):
    title = 'Ice Static'
    note = ['8-bit']

    #process
    def run(self, ips, imgs, para = None):
        conts = find_contours(ips.img, 1e-6, fully_connected='low', positive_orientation='low')
        trans = np.array(ips.info['trans']).reshape((2,3))

        xian = 'PROJCS["Xian 1980 / Gauss-Kruger zone 17", GEOGCS["Xian 1980",DATUM["Xian_1980",SPHEROID["Xian  1980",6378140,298.257,AUTHORITY["EPSG","7049"]],AUTHORITY["EPSG","6610"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4610"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",120],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","2331"]]'

        osrprj = osr.SpatialReference()
        osrprj.ImportFromWkt(ips.info['proj'])
        osrgeo = osr.SpatialReference()
        osrgeo.ImportFromWkt(xian)
        ct = osr.CoordinateTransformation(osrprj, osrgeo)

        data = []
        for i in range(len(conts)):
            cur = conts[i][:,::-1]
            jw = np.dot(trans[:,1:], cur.T).T+ trans[:,0]
            xy = ct.TransformPoints(jw)
            polygon = Polygon(xy)
            line = [i, polygon.area, polygon.centroid.x, polygon.centroid.y]
            data.append([round(j) for j in line])

        # IPy.table(ips.title+'-region', data, ['ID', 'Area', 'Center-X', 'Center-Y'])
        IPy.show_table(pd.DataFrame(data, columns=['ID', 'Area', 'Center-X', 'Center-Y']), ips.title+'-region')
        wx.CallAfter(pub.sendMessage, 'showicehist', areas=[i[1] for i in data])

class ShapeWriter(Simple):
    title = 'Export To Shapefile'
    note = ['8-bit']

    #process
    def run(self, ips, imgs, para = None):
        folder = IPy.getpath('Export Shapefile', '', 'open')
        if folder==None: return
        conts = find_contours(ips.img, 1e-6, fully_connected='low', positive_orientation='low')
        trans = np.array(ips.info['trans']).reshape((2,3))

        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","NO")    
        gdal.SetConfigOption("SHAPE_ENCODING","")     
        ogr.RegisterAll()    
        driver = ogr.GetDriverByName('ESRI Shapefile')  
        ds=driver.CreateDataSource(folder)  
        shapLayer=ds.CreateLayer("ice", geom_type=ogr.wkbPolygon)
        fieldDefn = ogr.FieldDefn('id', ogr.OFTString)   
        fieldDefn.SetWidth(4)  
        shapLayer.CreateField(fieldDefn);   
        defn = shapLayer.GetLayerDefn() 

        for i in range(len(conts)):
            cur = conts[i][:,::-1]
            jw = np.dot(trans[:,1:], cur.T).T+ trans[:,0]
            polygon = Polygon(jw)
            feature = ogr.Feature(defn) ;  
            feature.SetField('ID', i)  
            poly = ogr.CreateGeometryFromWkt(polygon.wkt)
            feature.SetGeometry(poly);  
            shapLayer.CreateFeature(feature)
            feature.Destroy()

class WKTWriter(Simple):
    title = 'Export To WKT'
    note = ['8-bit']

    #process
    def run(self, ips, imgs, para = None):
        folder = IPy.getpath('Export WKT', 'files (*.wkt)|*.wkt', 'save')
        if folder==None: return
        conts = find_contours(ips.img, 1e-6, fully_connected='low', positive_orientation='low')
        trans = np.array(ips.info['trans']).reshape((2,3))
        f = open(folder, 'w')
        for i in range(len(conts)):
            cur = conts[i][:,::-1]
            jw = np.dot(trans[:,1:], cur.T).T+ trans[:,0]
            polygon = Polygon(jw)
            f.write(polygon.wkt)
            f.write('\n')
        f.close()

def showice(img, ices, areas, para):
    plt.figure('Ice Segment')
    plt.imshow(img)
    patches = []
    for xy, c in zip(ices, areas):
        path = mpath.Path(xy[:,::-1])
        patch = mpatches.PathPatch(path, lw=1)
        patches.append(patch)
        #plt.gca().add_patch(patch)

    ps = PatchCollection(patches, alpha=255, cmap=plt.cm.rainbow)
    ps.set_array(areas)
    plt.gca().add_collection(ps)
    plt.gcf().colorbar(ps, ax=plt.gca())
    plt.grid()
    myfont = fm.FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
    plt.title(para['title'], fontproperties=myfont, size=24)
    plt.show()

pub.subscribe(showice, 'showice')

class ShowResult(Simple):
    title = 'Show Ice Result'
    note = ['8-bit']
    para = {'title':'海冰分布图  2017-00-00 00:00:00'}
    view = [(str,'title', 'title',  '')]

    #process
    def run(self, ips, imgs, para = None):
        conts = find_contours(ips.img, 1e-6, fully_connected='low', positive_orientation='low')
        trans = np.array(ips.info['trans']).reshape((2,3))
        xian = 'PROJCS["Xian 1980 / Gauss-Kruger zone 17", GEOGCS["Xian 1980",DATUM["Xian_1980",SPHEROID["Xian  1980",6378140,298.257,AUTHORITY["EPSG","7049"]],AUTHORITY["EPSG","6610"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4610"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",120],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","2331"]]'

        osrprj = osr.SpatialReference()
        osrprj.ImportFromWkt(ips.info['proj'])
        osrgeo = osr.SpatialReference()
        osrgeo.ImportFromWkt(xian)
        ct = osr.CoordinateTransformation(osrprj, osrgeo)

        areas = []
        for i in conts:
            cur = i[:,::-1]
            jw = np.dot(trans[:,1:], cur.T).T+ trans[:,0]
            xy = ct.TransformPoints(jw)
            areas.append(Polygon(xy).area)

        areas = np.array(areas)
        #areas[np.argmin(areas)] = areas.max()/-2
        wx.CallAfter(pub.sendMessage, 'showice', img=ips.info['back'], ices=conts, areas=areas, para=para)

class Difference(Simple):
    """Calculator Plugin derived from imagepy.core.engine.Simple """
    title = 'Ice Difference'
    note = ['8-bit']
    para = {'temp':None}
    
    view = [('img', 'temp', 'object', '')]

    def run(self, ips, imgs, para = None):
        ips2 = WindowsManager.get(para['temp']).ips
        nimg = ips.img * 0
        nimg[ips.img>0] += 80
        nimg[ips2.img>0] += 160
        ips = ImagePlus([nimg], ips.title+'-diff-'+ips2.title)
        ips.info = ips2.info
        IPy.show_ips(ips)

plgs = [Difference, IceStatic, ShowResult, ShapeWriter, WKTWriter]