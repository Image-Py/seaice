from imagepy.core.engine import Simple, Filter
from imagepy.core import ImagePlus
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from imagepy import IPy

class Reflectivity(Simple):
    title = 'Reflectivity'
    note = ['rgb', 'not_chanels']
    para = {'cn1':0.372, 'cn3':0.436, 'cn4':0.227}
    view = [(float, 'cn1', (0,1), 3, 'channel 1', '620—670 um'),
            (float, 'cn3', (0,1), 3, 'channel 3', '459-479 um'),
            (float, 'cn4', (0,1), 3, 'channel 4', '545-565 um')]
    
    #process
    def run(self, ips, imgs, para = None):
        r, g, b = ips.img.T
        cn1, cn3, cn4 = para['cn1'], para['cn3'], para['cn4']
        Av = (r * cn1 + b * cn3 + g * cn4).T
        Av = np.clip(Av, 0, 155).astype(np.uint8)
        av_ips = ImagePlus([Av.astype(np.uint8)], ips.title + '-Reflectivity')
        av_ips.info = ips.info
        IPy.show_ips(av_ips)

class Concentraion(Filter):
    title = 'Concentraion'
    note = ['8-bit', 'auto_snap', 'preview']
    para = {'water':0.04, 'ice':0.29}
    view = [('slide', 'water', (0,1), 3, 'pure water'),
            ('slide', 'ice', (0,1), 3, 'pure ice')]

    def run(self, ips, snap, img, para = None):
        lut = np.arange(256)/255.0 - para['water']
        lut *= 99/(para['ice'] - para['water'])
        img[:] = np.clip(lut, 0, 99).astype(np.uint8)[snap]

class Show(Simple):
    asyn = False
    title = 'Show Concentraion'
    note = ['8-bit']
    para = {'title':'密集度  2017-00-00 00:00:00'}
    view = [(str,'title', 'title',  '')]

    def run(self, ips, imgs, para):
        levels = np.arange(0,100,10)
        cmap = plt.cm.get_cmap(plt.cm.ocean, len(levels) - 1)
        plt.gca().set_aspect('equal')
        plt.contourf(ips.img[::-1], levels, cmap=cmap)
        plt.colorbar()
        myfont = fm.FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
        plt.title(para['title'], fontproperties=myfont, size=24)
        plt.show()

plgs = [Reflectivity, Concentraion, Show]