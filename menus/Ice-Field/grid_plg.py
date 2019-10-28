from imagepy import IPy, root_dir
import numpy as np
from imagepy.core.engine import Simple, Filter, Tool, Table
from imagepy.core.manager import ImageManager,TableManager, WriterManager
from imagepy.core.util import tableio
from imagepy.core.mark import GeometryMark
from imagepy.core import ImagePlus
from skimage.draw import polygon 
import pandas as pd
import gdal, wx, os
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
        from time import time
        lons = np.arange(para['longtitude_min']-para['longtitude_inter']/2,
            para['longtitude_max']+para['longtitude_inter']/2+1e-8, para['longtitude_inter'])
        lats = np.arange(para['latitude_min']-para['latitude_inter']/2, 
            para['latitude_max']+para['latitude_inter']/2+1e-8, para['latitude_inter'])[::-1]
        idx = np.array(np.where(np.ones((len(lats)-1, len(lons)-1)))).T.reshape((-1,1,2))
        idx = (idx + [(0,0),(1,0),(1,1),(0,1)]).reshape(-1,2).T
        arr = np.array([lons[idx[1]], lats[idx[0]]])
        trans = ips.img.mat
        arr = np.dot(np.linalg.inv(trans[:,1:]), arr-trans[:,:1]).T
        lines = [[(lons.min(), i),(lons.max(), i)] for i in lats]
        lines += [[(i, lats.min()),(i, lats.max())] for i in lons]
        lines = np.array(lines).reshape((-1,2)).T
        lines = np.dot(np.linalg.inv(trans[:,1:]), lines-trans[:,:1]).T
        return arr.reshape((-1,4,2)), lines, len(lats)-1, len(lons)-1

        '''
        print(arr)

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
        print('grid', time()-a)
        print(lines[0][:2])
        '''

    def preview(self, ips, para):
        grid, lines, row, col = self.grid(ips, para)
        lines = lines.reshape((-1,2,2))
        polygons = {'type':'lines', 'body':lines}
        ips.mark = GeometryMark(polygons)
        ips.update()

    def run(self, ips, snap, img, para = None):
        icemsk = ips.get_msk()
        grid, lines, row, col = self.grid(ips, para)
        from time import time
        a = time()
        mjd = []
        for pts in grid:
            msk = polygon(* pts.T[::-1], shape=img.shape[:2])
            inice = icemsk[msk]>0
            if inice.sum()<=len(msk[0])//2: mjd.append(-3)
            else:mjd.append(img[msk[0][inice], msk[1][inice]].mean())
            #ips.img[msk[0], msk[1]] = 0
        data = np.array(mjd).reshape(row, col)
        print('value', time()-a)
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

def write(path, df, title):
    values = df.values
    f = open(path, 'w')
    f.write(title+'\n')
    for line in values[:,:15]:
        f.write(('%2d'*len(line)+'\n')%tuple(line))
    for line in values[:,15:]:
        f.write(('%2d'*len(line)+'\n')%tuple(line))
    f.close()

class SaveField(Table):
    title = 'Save Fields'
    note = ['all']
    para={'path':root_dir}

    def show(self):
        filt = '|'.join(['%s files (*.%s)|*.%s'%(i.upper(),i,i) for i in ['']])
        return IPy.getpath('Save..', filt, 'save', self.para, name=self.tps.title[:8])

    #process
    def run(self, tps, snap, data, para = None):
        fp, fn = os.path.split(para['path'])
        fn, fe = os.path.splitext(fn)
        write(para['path'], data, tps.title)

plgs = [GridValue, SaveField, Surface2D]