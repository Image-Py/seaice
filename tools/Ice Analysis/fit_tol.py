from wx.lib.pubsub import pub
import matplotlib.pyplot as plt
import wx
from scipy.stats import linregress
from imagepy import IPy
from imagepy.core.engine import Simple, Filter,Tool
# class Plugin(Tool):
import numpy as np
import pandas as pd
from skimage import draw
from .circle import Circle
from imagepy.core import ImagePlus
from wx.lib.pubsub import pub
def lineregress(thick,gray):
    # data=np.array(list(thick.values()))
    slope, intercept, r_value, p_value, std_err = linregress(thick,gray)
    return slope,intercept
def lineregress_plot(para):
    data,slope,intercept=para
    print(data)
    plt.plot(data[0],data[1], 'ro')
    plt.plot(np.array(data[0]),slope*np.array(data[0])+intercept)
    plt.show()
pub.subscribe(lineregress_plot, 'lineregress_plot')
# 'tab'
class Plugin(Circle):
    title = 'fit'
    def lineregress(self,ips):
        thick=self.body[1]['z']
        gray=[self.get_gray(ips.imgs[0].copy(),i) for i in self.body[0]['body']]
        print(thick,gray)
        slope,intercept=lineregress(thick,gray)
        print(slope,intercept)
        a=np.arange(256)
        IPy.show_table(pd.DataFrame(np.array([a,slope*a+intercept])),title='temp')
        wx.CallAfter(pub.sendMessage, 'lineregress_plot', para=([thick,gray],slope,intercept))

    def get_mask(self,img,data):
        shape=img.shape
        msk=np.zeros(shape)
        rr, cc=draw.circle(data[1],data[0],data[2])
        msk[rr, cc] = 1
        # ipsd = ImagePlus([msk], 'test')
        # IPy.show_ips(ipsd)
        return msk.astype('uint8')
    def get_gray(self,img,circle_data):
        msk=self.get_mask(img,circle_data)
        img*=msk
        gray=img[img>0].mean()
        return gray
# class NewTool(Simple):
#     para = {'thickness':0}
#     view = [(float, 'thickness', (0,1000), 3, 'thickness', 'pix'),]
#     title = 'para'
#     note = [ 'all', 'preview']
#     def load(self, ips=None):
#         print('load')
#         if str(self.index) in self.parent.thick.keys():
#             self.para['thickness']=self.parent.thick[str(self.index)][1]
#         else:self.para['thickness']=0
#         return True
#     def preview(self, ips, para):
#         self.ok(self.ips)
#     def run(self, parent, doc, para):
#         self.parent.thick[str(self.index)]=[self.ips.gray_data[self.index],self.para['thickness']]
# class Plugin(Tool):
#     title = 'fit'
#     thick={}
#     def mouse_down(self, ips, x, y, btn,  **key):
#         print(x,y)
#         if btn==3:
#             slope,intercept=self.lineregress(self.thick)
#             print(slope,ips.gray_data,intercept)
#             # thick_out=ips.gray_data*slope+intercept
#             thick_out=ips.gray_data*np.array(slope)+np.array(intercept)
#             thick_out=thick_out.reshape(ips.grid_shape)[::-1,:]
#             # print(thick_out.reshape(ips.grid_shape))
#             IPy.show_table(pd.DataFrame(thick_out),title='temp')
#             wx.CallAfter(pub.sendMessage, 'lineregress_plot', para=(np.array(list(self.thick.values())),slope,intercept))
#             return 
#         index,i=self.pick(ips, x, y, btn)
#         if index:
#             # print(x,y,i)
#             pd1 = NewTool()
#             pd1.parent,pd1.index=self,i
#             pd1.ips=ips
#             pd1.start()  
#         else:print(self.thick)
#     def pick(self, ips, x, y, btn, **key):
#         lim=3
#         for i in range(len(ips.test_id['body'])):
#             ox,oy=ips.test_id['body'][i][0],ips.test_id['body'][i][1]
#             if abs(x-ox)<lim and abs(y-oy)<lim:return(True,i)
#         return (False,-1)
#     def mouse_move(self, ips, x, y, btn, **key):
#         index,i=self.pick(ips, x, y, btn)
#         if index==True:
#             self.cursor = wx.CURSOR_HAND
#             if str(i) in self.thick.keys():
#                 IPy.set_info('Gray:'+str(round(ips.gray_data[i],2))+',Thick:'+str(self.thick[str(i)]))
#             else:IPy.set_info('Gray:'+str(round(ips.gray_data[i],2))+',Thick:0')
#         else:self.cursor = wx.CURSOR_CROSS
#     def mouse_wheel(self, ips, x, y, d, **key):
#         pass
#     def lineregress(self,thick):
#         data=np.array(list(thick.values()))
#         slope, intercept, r_value, p_value, std_err = linregress(data[:,0], data[:,1])
#         return slope,intercept
# plgs = [Fit]