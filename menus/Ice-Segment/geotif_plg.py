import gdal
from imagepy.core.util import fileio
from imagepy.core.engine import Simple
from imagepy import IPy
from imagepy.core import ImagePlus
from imagepy.core.manager import WindowsManager
import geonumpy.io as gio
import os, os.path as osp
import scipy.ndimage as nimg
import numpy as np
from numpy.linalg import inv
import geonumpy.match as gmt

class OpenTif(fileio.Reader):
    title = 'Geo TIF Open'
    filt = ['TIF']

    def run(self, para = None):
        img = gio.read_tif(para['path'])
        fp, fn = osp.split(para['path'])
        fn, fe = osp.splitext(fn)
        IPy.show_img([img], fn)

class SaveTif(fileio.Writer):
    title = 'Geo TIF Write'
    filt = ['TIF']

    def run(self, ips, imgs, para = None):
        gio.write_tif(ips.img, ['path'])

class Match(Simple):
    """Calculator Plugin derived from imagepy.core.engine.Simple """
    title = 'Geo Match'
    note = ['all']
    para = {'temp':None}
    
    view = [('img', 'temp','template',  '')]

    def run(self, ips, imgs, para = None):
        temp = WindowsManager.get(para['temp']).ips
        rst = gmt.match_multi(imgs, temp.img.getbox())
        IPy.show_img([rst], ips.title+'-match')

plgs = [OpenTif, SaveTif, Match]