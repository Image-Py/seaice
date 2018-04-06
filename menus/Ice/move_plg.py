import wx
from imagepy.core.engine import Filter, Simple, Tool
from imagepy.core.manager import WindowsManager
from .matcher import Matcher
from scipy.ndimage import gaussian_filter
import numpy as np
from numpy.linalg import norm
from imagepy import IPy
from skimage.feature import match_descriptors, ORB

#CVSURF = cv2.xfeatures2d.SURF_create if cv2.__version__[0] =="3" else cv2.SURF

def anglex(x, y):
    ang = np.arccos(x/norm([x,y]))
    return ang if y>=0 else np.pi*2-ang

class Mark:
    def __init__(self, data, o):
        self.data = data
        self.o = (o[0]/2, o[1]/2)

    def draw(self, dc, f, **key):
        
        dc.SetTextForeground((255,255,0))
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, 
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        dc.SetFont(font)
        trans = self.data[key['cur']]
        if trans is None: 
            dc.DrawText(u'当前速度', 10, 10)
            return

        pts = [np.array([self.o[0], self.o[1], 1])]
        for i in range(50):
            pts.append((trans*np.mat(pts[-1]).T).A1)
        
        ta = trans.A1
        v = pts[1] - pts[0]
        dc.DrawText(u'当前速度:%.3f'%(norm([v[0], v[1]])), 10, 10)
        dc.DrawText(u'当前方向:%d'%(anglex(v[0], v[1])/np.pi*180), 10, 30)
        dc.DrawText(u'旋转分量:%.3f'%(anglex(ta[0], abs(ta[1]))/np.pi*180), 10, 50)

        dc.SetPen(wx.Pen((255,255,0), width=1, style=wx.SOLID))
        dc.SetBrush(wx.Brush((0,0,0), wx.BRUSHSTYLE_TRANSPARENT))
        pos = f(*(self.o[1], self.o[0]))
        for i in range(5):
            dc.DrawCircle(pos[0], pos[1], i*30)
        dc.SetPen(wx.Pen((0,255,0), width=1, style=wx.SOLID))
        dc.SetBrush(wx.Brush((255,0,0)))
        dc.DrawLines([f(*i[1::-1]) for i in pts])
        for pos in pts[::5]:
            pos = f(*(pos[1], pos[0]))
            dc.DrawCircle(pos[0], pos[1], 2)

class Plugin(Simple):
    title = 'Moving Detect'
    note = ['8-bit', 'stack']

    #parameter
    para = {'ds':10, 'sigma':3, 'std':1}

    view = [(int, (1, 1000), 0, 'simple', 'ds', ''),
            (int, (1, 10), 0, 'sigma', 'sigma', 'pix'),
            (int, (1, 5), 0, 'Std', 'std', 'tor')]

    #process
    def run(self, ips, imgs, para = None):
        kfs, mats = [], []
        ds, std = para['ds'], para['std']/100.0
        data = []
        descriptor_extractor = ORB(n_keypoints=500)
        for i in range(len(imgs)):
            self.progress(i, len(imgs))
            #kps, feats = detector.detectAndCompute(imgs[i][::ds,::ds], None)
            img = gaussian_filter(imgs[i][::ds,::ds], para['sigma'])
            descriptor_extractor.detect_and_extract(img)
            kps = descriptor_extractor.keypoints
            feats = descriptor_extractor.descriptors
            if len(kfs)>0:
                matcher = Matcher(6, std)
                idx, msk, m = matcher.filter(kfs[-1][0], kfs[-1][1], kps, feats)
                orim = matcher.get_ori_trans(1/para['ds'])
                if msk.sum()>30:
                    mats.append(orim)
                    data.append(orim.A1[:6].round(4))
                else: 
                    mats.append(None)
                    data.append(['--']*6)
            kfs.append((kps, feats))
            
        mats.append(None)
        data.append(['--']*6)
        ips.mark = Mark(mats, imgs[0].shape)
        titles = ['KX','RX','OffX','RY','KY','OffY']
        IPy.table(ips.title+'-moveing', data, titles)

