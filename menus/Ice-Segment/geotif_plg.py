import gdal
from imagepy.core.util import fileio
from imagepy.core.engine import Simple
from imagepy import IPy
from imagepy.core import ImagePlus
from imagepy.core.manager import WindowsManager
import os
import scipy.ndimage as nimg
import numpy as np
from numpy.linalg import inv

class Open(fileio.Reader):
	title = 'Geo TIF Open'
	filt = ['TIF', 'TIFF']

	#process
	def run(self, para = None):
		dataset = gdal.Open(para['path'])
		imgs = dataset.ReadAsArray().transpose((1,2,0))
		fp, fn = os.path.split(para['path'])
		fn, fe = os.path.splitext(fn) 
		ips = ImagePlus([imgs], fn)
		IPy.show_ips(ips)

		ips.info['proj'] = dataset.GetProjection()
		ips.info['trans'] = dataset.GetGeoTransform()
		cont = '##Projection:\n%s\n##Transform\n%s\n'
		IPy.show_md(fn, cont%(ips.info['proj'], ips.info['trans']))
		
class Save(fileio.Writer):
    title = 'Geo TIF Save'
    filt = ['TIF', 'TIFF']

    #process
    def run(self, ips, imgs, para = None):
        im_data = ips.img.transpose((2,0,1))

        im_bands, im_height, im_width = im_data.shape
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(para['path'], im_width, im_height, im_bands, gdal.GDT_Byte)
        if(dataset!= None):
            dataset.SetGeoTransform(ips.info['trans']) #写入仿射变换参数
            dataset.SetProjection(ips.info['proj']) #写入投影
        for i in range(im_bands):
            dataset.GetRasterBand(i+1).WriteArray(im_data[i])
        del dataset

class DuplicatePrj(Simple):
    title = 'Duplicate With Projection'
    note = ['all']
    
    para = {'name':'Undefined'}
    
    def load(self, ips):
        self.para['name'] = ips.title+'-copy'
        self.view = [(str, 'name','Name', '')]
        return True
    #process
    def run(self, ips, imgs, para = None):
        name = para['name']
        if ips.roi == None:
            img = ips.img.copy()
            ipsd = ImagePlus([img], name)
            ipsd.backimg = ips.backimg
        else:
            img = ips.get_subimg().copy()
            ipsd = ImagePlus([img], name)
            box = ips.roi.get_box()
            ipsd.roi = ips.roi.affine(np.eye(2), (-box[0], -box[1]))
            if not ips.backimg is None:
                sr, sc = ips.get_rect()
                ipsd.backimg = ips.backimg[sr, sc]

        ipsd.backmode = ips.backmode
        ipsd.info = dict(ips.info)
        trans = np.array(ips.info['trans']).reshape((2,3))
        sc, sr = ips.get_rect()
        dal = np.dot(trans[:,1:], (sr.start, sc.start))
        trans[:,0] += dal
        ipsd.info['trans'] = tuple(trans.ravel())
        ipsd.info['back'] = ipsd.img.copy()
        IPy.show_ips(ipsd)

class Match(Simple):
    """Calculator Plugin derived from imagepy.core.engine.Simple """
    title = 'Geo Match'
    note = ['all']
    para = {'temp':None}
    
    view = [('img', 'temp','template',  '')]

    def run(self, ips, imgs, para = None):
        ips2 = WindowsManager.get(para['temp']).ips
        trans1 = np.array(ips.info['trans'])
        trans1 = np.hstack((trans1[[1,2,0,4,5,3]], [0,0,1]))
        trans1 = trans1.reshape((3,3))
        trans2 = np.array(ips2.info['trans'])
        trans2 = np.hstack((trans2[[1,2,0,4,5,3]], [0,0,1]))
        trans2 = trans2.reshape((3,3))

        trans = np.dot(inv(trans1), trans2)[:2][::-1]
        trans[:,[0,1]] = trans[:,[1,0]]
        if ips.img.ndim == 2:
            rst = nimg.affine_transform(ips.img, trans[:,:2], 
                offset=trans[:,2], output_shape=ips2.size)
        else:
            rst = np.zeros(ips2.size+(3,), dtype=np.uint8)
            for i in (0,1,2):
                nimg.affine_transform(ips.img[:,:,i], trans[:,:2], 
                    offset=trans[:,2], output_shape=ips2.size, output=rst[:,:,i])
        ips = ImagePlus([rst], ips.title+'-trans')
        ips.info = ips2.info
        IPy.show_ips(ips)

plgs = [Open, Save, DuplicatePrj, Match]