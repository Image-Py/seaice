from imagepy import IPy
import numpy as np
from imagepy.core.engine import Simple, Filter, Tool, Table
from imagepy.core.manager import ImageManager,TableManager, WriterManager
from imagepy.core.util import tableio
from imagepy.core.mark import GeometryMark
from imagepy.core import ImagePlus
from skimage.draw import polygon 
import pandas as pd
import gdal, wx
from imagepy.core import myvi

class GridValue(Filter):
    title = 'Count Grid Field'
    note = ['8-bit', 'req_roi', 'preview']
    view = [(float, 'longtitude_max', (-180,180), 8, 'longtitude_max', 'degree'),
            (float, 'longtitude_min', (-180,180), 8, 'longtitude_min', 'degree'),
            (float, 'latitude_max',(-90,90), 8, 'latitude_max', 'degree'),
            (float, 'latitude_min',(-90,90), 8, 'latitude_min', 'degree'),
            (float, 'latitude_inter',(0,100), 3, 'latitude_inter', 'degree'),
            (float, 'longtitude_inter',(0,100), 3, 'longtitude_inter', 'degree')]
            # (float, 'e', (-100,100), 1, 'eccentricity', 'ratio')
    para = {'longtitude_max':124.5, 'longtitude_min':117.5,'latitude_max':41,
        'latitude_min':37, 'latitude_inter':0.100,'longtitude_inter':0.100}
    # def load(self, ips):pass

    def grid(slef, ips, para):
        lons = np.arange(para['longtitude_min']-para['longtitude_inter'], 
            para['longtitude_max']+para['longtitude_inter']+1e-8, para['longtitude_inter'])
        lats = np.arange(para['latitude_min']-para['latitude_inter'], 
            para['latitude_max']+para['latitude_inter']+1e-8, para['latitude_inter'])[::-1]
        trans = np.array(ips.info['trans']).reshape((2,3))
        lines = []
        jw2pix = lambda trans, i : np.dot(i-trans[:,0], np.linalg.inv(trans[:,1:]))
        for r in range(len(lats)-1):
            line = []
            for c in range(len(lons)-1):
                p1, p2 = (lons[c],lats[r]),(lons[c],lats[r+1])
                p3, p4 = (lons[c+1],lats[r+1]),(lons[c+1],lats[r])
                rect = [jw2pix(trans, i) for i in [p1, p2, p3, p4]]
                line.append([tuple(i) for i in rect])
            lines.append(line)
        return lines

    def preview(self, ips, para):
        lines = self.grid(ips, para)
        polygon_data = []
        for i in lines: polygon_data.extend(i)
        polygons = {'type':'polygons', 'body':polygon_data}
        ips.mark = GeometryMark(polygons)
        ips.update = True

        
    def run(self, ips, snap, img, para = None):
        icemsk = ips.get_msk()
        lines = self.grid(ips, para)
        mjd = []
        for line in lines:
            for pts in line:
                msk = polygon(* np.array(pts).T[::-1], shape=img.shape[:2])
                inice = icemsk[msk]>0
                if inice.sum()==0: mjd.append(-3)
                else:mjd.append(img[msk[0][inice], msk[1][inice]].mean())
                #ips.img[msk[0], msk[1]] = 0
        data = np.array(mjd).reshape((len(lines), len(lines[0])))
        IPy.show_table(pd.DataFrame(data), title=ips.title+'-Field')

class Surface2D(Table):
    title = 'Show Fields 3D'
    para = {'name':'undifine', 'h':1}
    view = [(str, 'name', 'Name', ''),
            (float, 'h', (0.01,1), 2, 'scale z', '0.01~1')]
    
    def load(self, para):
        self.frame = myvi.Frame3D.figure(IPy.curapp, title='3D Canvas')
        return True

    def run(self, tps, data, snap, para = None):
        vts, fs, ns, cs = myvi.build_surf2d(tps.data.values, ds=1, sigma=0, k=para['h'])
        self.frame.viewer.add_surf_asyn(para['name'], vts, fs, ns, cs)
        self.frame.Raise()
        self.frame = None

def write(path, df):
    values = df.values
    f = open(path, 'w')
    for line in values[:,:15]:
        f.write(('%2d'*len(line)+'\n')%tuple(line))
    for line in values[:,15:]:
        f.write(('%2d'*len(line)+'\n')%tuple(line))
    f.close()

class SaveField(tableio.Writer):
    title = 'Save Fields'
    filt = ['']

save_excel = lambda path, data:data.to_excel(path)

WriterManager.add([''], write, tag='tab')

plgs = [GridValue, SaveField, Surface2D]