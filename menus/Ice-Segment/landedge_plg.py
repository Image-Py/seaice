from imagepy.core.engine import Simple
from imagepy.core.roi import PolygonRoi, roiio
from imagepy.core.manager import RoiManager
from osgeo import osr
from imagepy import IPy
from os import path as osp
from numpy.linalg import inv
import numpy as np

class Open(Simple):
    title = 'Open Geo Roi'
    note = ['all']
    para = {'path':''}

    def check(self, ips):
        if not Simple.check(self, ips): return False
        if not 'trans' in ips.data:
            IPy.alert('No geotransform found!')
        else: return True

    def show(self):
        filt = '|'.join(['%s files (*.%s)|*.%s'%(i.upper(),i,i) for i in ['wkt']])
        return IPy.getpath('Save..', filt, 'open', self.para)

    #process
    def run(self, ips, imgs, para = None):
        roi = roiio.readwkt(para['path'])
        f = open(para['path'].replace('.wkt', '.prj'))
        proj = f.read()
        f.close()
        prjd = osr.SpatialReference()
        prjd.ImportFromWkt(ips.data['proj'])
        prjs = osr.SpatialReference()
        prjs.ImportFromWkt(proj)
        ct = osr.CoordinateTransformation(prjs, prjd)
        m = np.array(ips.data['trans']).reshape(2,3)

        def trans(x, y):
            xy = ct.TransformPoints(np.array([x, y]).T)
            return np.dot(inv(m[:,1:]), np.array(xy).T[:2]-m[:,:1])

        ips.roi = roi.transform(trans)
        if 'back' in ips.data:ips.roi.fill(ips.data['back'], (0,0,80))

class Save(Simple):
    title = 'Save Geo Roi'
    note = ['all', 'req_roi']
    para={'path':''}

    def check(self, ips):
        if not Simple.check(self, ips): return False
        if not 'trans' in ips.data:
            IPy.alert('No geotransform found!')
        else: return True

    def show(self):
        filt = '|'.join(['%s files (*.%s)|*.%s'%(i.upper(),i,i) for i in ['wkt']])
        return IPy.getpath('Save..', filt, 'save', self.para)

    def run(self, ips, imgs, para = None):
        trans = np.array(ips.data['trans']).reshape((2,3))
        roiio.savewkt(ips.roi.affine(trans[:,1:], trans[:,0]), para['path'])
        f = open(para['path'].replace('.wkt', '.prj'), 'w')
        f.write(ips.data['proj'])
        f.close()

class Add2Manager(Simple):
    """Add2Manager: derived from imagepy.core.engine.Simple """
    title = 'Add To Geo Manager'
    note = ['all', 'req_roi']
    para = {'name':''}
    view = [(str,'name',  'Name', '')]

    def check(self, ips):
        if not Simple.check(self, ips): return False
        if not 'trans' in ips.data:
            IPy.alert('No geotransform found!')
        else: return True

    def run(self, ips, imgs, para = None):
        trans = np.array(ips.data['trans']).reshape((2,3))
        roi = ips.roi.affine(trans[:,1:], trans[:,0])
        RoiManager.add(para['name'], roi)
        
class LoadRoi(Simple):
    """LoadRoi: derived from imagepy.core.engine.Simple """
    title = 'Load Geo Roi'
    note = ['all']
    para = {'name':''}
    
    def check(self, ips):
        if not Simple.check(self, ips): return False
        if not 'trans' in ips.data:
            IPy.alert('No geotransform found!')
        else: return True

    def load(self, ips):
        titles = list(RoiManager.rois.keys())
        if len(titles)==0: 
            IPy.alert('No roi in manager!')
            return False
        self.para['name'] = titles[0]
        LoadRoi.view = [(list,'name', titles, str, 'Name',  '')]
        return True

    def run(self, ips, imgs, para = None):
        trans = np.array(ips.data['trans'])
        trans = np.hstack((trans[[1,2,0,4,5,3]], [0,0,1]))
        trans = inv(trans.reshape((3,3)))
        # lambda p:np.dot(inv(trans[:,1:]), (np.array(p)-trans[:,0]))
        # trans * p + offset
        roi = RoiManager.get(para['name'])
        ips.roi = roi.affine(trans[:2,:2], trans[:2,2])

plgs = [Add2Manager, LoadRoi, Open, Save]