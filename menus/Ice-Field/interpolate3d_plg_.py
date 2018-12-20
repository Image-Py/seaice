from scipy import interpolate
from imagepy.core.engine import Simple
from imagepy.core import myvi
import numpy as np
def bulid_data(data):
    # bulid_data(np.array([ips.data[1]['body'],ips.data[1]['z']]))
    z=data[1].astype(np.float64)
    data=np.array([i for i in data[0]])
    x,y,weight=data[:,0],data[:,1],data[:,2]
    tck = interpolate.bisplrep(x, y, z, w=weight,kx=1,ky=2)
    xnew, ynew = np.mgrid[0:500:500j, 0:500:500j]
    print('xynew',xnew,ynew)
    znew = interpolate.bisplev(xnew[:,0], ynew[0,:], tck)
    return znew
# data=np.load('test.npy')
def surface2d(z):
    vts, fs, ns, cs = myvi.util.build_surf2d(z, ds=1, k=20, sigma=2)
    cs[:] = myvi.util.auto_lookup(vts[:,2], myvi.util.linear_color('jet'))/255
    manager = myvi.Manager()
    manager.add_surf('dem', vts, fs, ns, cs)
    manager.show('DEM Demo') 
    
class Interpolate3d(Simple):
    title = 'interpolate 3d'
    note = ['all']
    
    # para = {'name':'Undefined'}
    
    def load(self, ips):
        print('in 3d')
        print(ips.data[1]['body'],ips.data[1]['z'])
        # np.save('test',np.array([ips.data[1]['body'],ips.data[1]['z']]))
        surface2d(bulid_data(np.array([ips.data[1]['body'],ips.data[1]['z']])))
        # surface2d(ips.data)

        # self.para['name'] = ips.title+'-copy'
        # self.view = [(str, 'name','Name', '')]
        # return True
    #process
    def run(self, ips, imgs, para = None):
        print('in 3d')
        print(ips.data)
plgs = [ Interpolate3d]