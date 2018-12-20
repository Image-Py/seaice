import wx, sys
import numpy as np
from numpy.linalg import norm
from scipy import interpolate
from imagepy.core.engine import Filter

if sys.version_info[0]==2:memoryview=np.getbuffer

class LinePanel(wx.Panel):
    """ HistCanvas: diverid from wx.core.Panel """
    def __init__(self, parent, hist=None, l=255):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, 
                            pos = wx.DefaultPosition, size = wx.Size(l*2+50, l+25), 
                            style = wx.TAB_TRAVERSAL )
        self.init_buf()
        self.offset = (35, 5)
        self.l, self.k = l, l/255.0
        self.idx = -1
        self.set_hist(hist)
        self.update = False
        self.ylim = 50
        self.pts = [(0,0), (255, 255)]
        wx.Panel.Bind(self, wx.EVT_SIZE, self.on_size)  
        wx.Panel.Bind(self, wx.EVT_IDLE, self.on_idle)
        wx.Panel.Bind(self, wx.EVT_PAINT, self.on_paint)
        wx.Panel.Bind(self, wx.EVT_LEFT_DOWN, self.on_ld)
        wx.Panel.Bind(self, wx.EVT_LEFT_UP, self.on_lu )
        wx.Panel.Bind(self, wx.EVT_MOTION, self.on_mv )
        wx.Panel.Bind(self, wx.EVT_RIGHT_DOWN, self.on_rd )
        wx.Panel.Bind(self, wx.EVT_MOUSEWHEEL, self.on_wl )

    @classmethod
    def lookup(cls, pts):
        x, y = np.array(pts).T
        kind = 'linear' if len(pts)==2 else 'quadratic'
        f = interpolate.interp1d(x, y, kind='linear')
        return np.clip(f(np.arange(256)),0,255).astype(np.uint8)
            
    def init_buf(self):
        box = self.GetClientSize()
        self.buffer = wx.Bitmap(box.width, box.height)
        
    def on_size(self, event):
        self.init_buf()
        self.update = True
        
    def on_idle(self, event):
        if self.update == True:
            self.draw()
            self.update = False

    def pick(self, x, y):
        dis = norm(np.array(self.pts)-(x,y), axis=1)
        if dis[np.argmin(dis)] > 3: return -1
        return np.argmin(dis)

    def on_ld(self, event):
        x = (event.GetX()-self.offset[0])/self.k 
        y = (event.GetY()-self.offset[1])/self.k
        self.idx = self.pick(x/2, 255-y)
        if self.idx==-1: 
            self.pts.append((x/2, 255-y))
            self.idx = len(self.pts)-1
            self.update = True
            self.handle(event)

    def on_lu(self, event):
        self.idx = -1

    def on_rd(self, event):
        x = (event.GetX()-self.offset[0])/self.k 
        y = (event.GetY()-self.offset[1])/self.k
        self.idx = self.pick(x/2, 255-y)
        if self.idx==-1: return
        if not self.pts[self.idx][0] in (0, 255):
            del self.pts[self.idx]
            self.idx = -1
            self.update = True
            self.handle(event)

    def on_mv(self, event):
        x = (event.GetX()-self.offset[0])/self.k 
        y = (event.GetY()-self.offset[1])/self.k
        if self.pick(x/2, 255-y)!=-1:
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        else: self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        if self.idx!=-1:
            oldx = self.pts[self.idx][0]
            if oldx == 0: x=0
            elif oldx==255: x=255*2
            else: x = np.clip(x, 1, 254+255)
            y = np.clip(y, 0, 255)
            self.pts[self.idx] = (x/2, 255-y)
            self.update = True
            self.handle(event)
    
    def on_wl(self, event):
        if self.idx!=-1:
            x, y = self.pts[self.idx]
            self.pts[self.idx] = (x, y+[-1,1][event.GetWheelRotation()>0])
            self.update = True
            self.handle(event)

    def on_paint(self, event):
        wx.BufferedPaintDC(self, self.buffer)
        
    def set_hist(self, hist):
        if hist is None:self.hist=None
        else:
            self.hist = (hist*self.l/hist.max())
            self.logh = (np.log(self.hist+1.0))*(self.l/(np.log(self.l+1)))
        self.update = True
        
    def set_pts(self, pts):
        self.x1, self.x2 = x1, x2
        self.update = True        

    def draw(self):
        ox, oy = self.offset
        # get client device context buffer
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()
        # w, h = self.GetClientSize()
        # the main draw process 
        
        if not self.hist is None:      
            dc.SetPen(wx.Pen((200,200,200), width=1, style=wx.SOLID))
            for i in np.linspace(0,self.l,256).astype(np.int16):
                dc.DrawLine(i*2+ox,self.l+1+oy,i*2+ox,self.l+1-self.logh[i]+oy)
                dc.DrawLine(i*2+1+ox,self.l+1+oy,i*2+1+ox,self.l+1-self.logh[i]+oy)
            dc.SetPen(wx.Pen((100,100,100), width=1, style=wx.SOLID))
            for i in np.linspace(0,self.l,256).astype(np.int16):
                dc.DrawLine(i*2+ox,self.l+1+oy,i*2+ox,self.l+1-self.hist[i]+oy)
                dc.DrawLine(i*2+1+ox,self.l+1+oy,i*2+1+ox,self.l+1-self.hist[i]+oy)
        x, y = np.array(self.pts).T
        kind = 'linear' if len(self.pts)==2 else 'quadratic'
        f = interpolate.interp1d(x, y, kind='linear')
        ys = np.clip(f(np.linspace(0, 255, self.l*2+1)), 0, 255)
        if ys is None:return
        dc.SetBrush(wx.Brush((0,0,0)))
        dc.SetPen(wx.Pen((0,0,0), width=1))
        for i in self.pts: 
            dc.DrawCircle(i[0]*self.k*2+ox+1, round(self.l+1-i[1]*self.k+oy), 2)
            dc.DrawText('%d,%.1f'%(i[0], i[1]/255*self.ylim), round(i[0]*self.k*2+ox), round(self.l+1-i[1]*self.k+oy)-20)

        xs, ys = np.linspace(0, self.l, self.l*2+1)*2+ox, self.l+1-ys*self.k+oy
        dc.DrawPointList(list(zip((xs).round(), ys.round())))

        dc.SetPen(wx.Pen((0,0,0), width=1, style=wx.SOLID))
        for i in np.linspace(0, self.l+1, 5):
            dc.DrawLine(0*2+ox-3, i+oy, self.l*2+2+ox, i+oy)
            dc.DrawLine(i*2+ox, 0+oy, i*2+ox, self.l+2+oy+3)
            dc.DrawText('10.5', 5, i+oy-8)
            dc.DrawText('255', i*2+ox-8, self.l+2+oy+3)
        dc.SetBrush(wx.Brush((0,0,0), wx.BRUSHSTYLE_TRANSPARENT))
        '''
        arr = np.zeros((10,self.l+1,3),dtype=np.uint8)
        arr[:] = np.vstack([np.linspace(0,255,self.l+1)]*3).T
        bmp = wx.Bitmap.FromBuffer(self.l+1,10, memoryview(arr))
        dc.DrawBitmap(bmp, 0+ox, self.l+6+oy)
        dc.DrawRectangle(0+ox, self.l+6+oy, self.l*2+1, 10)
        arr = arr.transpose((1,2,0))[::-1].copy()
        bmp = wx.Bitmap.FromBuffer(10, self.l+1, memoryview(arr))
        dc.DrawBitmap(bmp, -15+ox, 0+oy)
        dc.DrawRectangle(-15+ox, 0+oy, 10, self.l+1)
        '''
        
    def handle(self, event):pass
    
    def Bind(self, z, handle):self.handle = handle

    def SetValue(self, value=None):
        print('here', value)
        if not value is None:
            self.pts = value
        else: self.pts = [(0,0), (255, 255)]
        self.update = True

    def GetValue(self): return [(i[0], i[1]/255*self.ylim) for i in sorted(self.pts)]


        

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None)
    hist = CurvePanel(frame, l=255)
    frame.Fit()
    frame.Show(True)
    hist.set_hist(np.random.rand(256)+2)
    app.MainLoop() 