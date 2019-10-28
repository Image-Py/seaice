from imagepy import IPy
from imagepy.core import ImagePlus
import wx
import numpy as np
from imagepy.core.engine import Simple, Free
from imagepy.core.manager import WindowsManager, ImageManager
from scipy.ndimage import label, generate_binary_structure
from skimage.measure import regionprops
from shapely.geometry import Polygon, Point
from shapely.affinity import affine_transform
from skimage.measure import find_contours
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from imagepy.core.util import fileio
from matplotlib.collections import PatchCollection
import matplotlib.font_manager as fm
from wx.lib.pubsub import pub
import osr, gdal, ogr
import pandas as pd
import geopandas as gpd
import geonumpy.io as gio

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
    note = ['all']

    #process
    def run(self, ips, imgs, para = None):
        conts = find_contours(ips.img, 1e-6, fully_connected='low', positive_orientation='low')
        m = ips.img.mat
        m = [m[0,1], 0, 0, m[1,2], m[0,0], m[1,0]]
        shps = [[Polygon(i[:,::-1])] for i in conts]
        gdf = gpd.GeoDataFrame(shps, columns=['geometry'], crs=ips.img.crs)
        g = gdf.geometry.transform(lambda x: affine_transform(x, m))
        g = g.transform(lambda x: affine_transform(x, [0,1,1,0,0,0])).to_crs(3857)
        gdf['ID'] = range(len(g))
        gdf['Area'] = g.area
        gdf['Center-X'] = gdf.centroid.x
        gdf['Center-Y'] = gdf.centroid.y
        IPy.show_table(gdf[['ID', 'Area', 'Center-X', 'Center-Y']], ips.title+'-region')
        wx.CallAfter(pub.sendMessage, 'showicehist', areas=g.area)

class ShapeWriter(fileio.Writer):
    title = 'Export To Shapefile'
    filt = ['SHP']

    #process
    def run(self, ips, imgs, para = None):
        conts = find_contours(ips.img, 1e-6, fully_connected='low', positive_orientation='low')
        m = ips.img.mat
        m = [m[0,1], 0, 0, m[1,2], m[0,0], m[1,0]]
        shps = [[Polygon(i[:,::-1])] for i in conts]
        gdf = gpd.GeoDataFrame(shps, columns=['geometry'], crs=ips.img.crs)
        g = gdf.geometry.transform(lambda x: affine_transform(x, m))
        g = g.transform(lambda x: affine_transform(x, [0,1,1,0,0,0])).to_crs(3857)
        gdf['geometry'] = g
        print(para)
        print(gdf.columns)
        gdf['ID'] = range(len(g))
        gdf['Area'] = g.area
        gdf['Center-X'] = gdf.centroid.x
        gdf['Center-Y'] = gdf.centroid.y
        gio.write_shp(gdf, para['path'])

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
    para = {'title':'海冰分布图  2017-00-00 00:00:00', 'background':None}
    view = [(str,'title', 'title',  ''),
            ('img', 'background', 'background', '')]

    #process
    def run(self, ips, imgs, para = None):
        conts = find_contours(ips.img, 1e-6, fully_connected='low', positive_orientation='low')
        areas = [Polygon(i).area for i in conts]
        areas = np.array(areas)
        img = ImageManager.get(para['background']).get_subimg()
        wx.CallAfter(pub.sendMessage, 'showice', img=img, ices=conts, areas=areas, para=para)

class Difference(Simple):
    """Calculator Plugin derived from imagepy.core.engine.Simple """
    title = 'Ice Difference'
    note = ['8-bit']
    para = {'temp':None}
    
    view = [('img', 'temp', 'object', '')]

    def run(self, ips, imgs, para = None):
        ips2 = ImageManager.get(para['temp'])
        nimg = ips.img * 0
        nimg[ips.img>0] += 80
        nimg[ips2.img>0] += 160
        ips = ImagePlus([nimg], ips.title+'-diff-'+ips2.title)
        IPy.show_ips(ips)

plgs = [Difference, IceStatic, ShowResult, ShapeWriter]