import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import solve
from imagepy import IPy
from imagepy.core.engine import Simple
import wx
class SetTrans(Simple):
    title = 'Set Trans'
    note = ['all']
    para = {'path':''}
    def run(self, ips, imgs, para = None):
        filt = "XML files (*.xml)|*.xml"
        print(IPy.getpath('Open..', filt, 'open', self.para))
        print(self.para['path'])
        data=self.GetGeoTransform(self.para['path'])
        trans=self.get_trans(data)
        print(trans)
    def GetGeoTransform(self,path):
        lst=['TopLeftLatitude','TopLeftLongitude','TopRightLatitude','TopRightLongitude',
            'BottomRightLatitude','BottomRightLongitude','BottomLeftLatitude','BottomLeftLongitude',
             'WidthInPixels','HeightInPixels']
        dic={}
        root = ET.parse(path).getroot()
        for i in lst:dic[i]=float(root.find(i).text)
        return dic
    def get_trans(self,dic):

        trans=np.zeros((2,3))
        trans[0,0],trans[1,0]=data['TopLeftLongitude'],data['TopLeftLatitude']
        m=np.array([[data['WidthInPixels'], 0], [data['WidthInPixels'] ,data['HeightInPixels']]])
        n=np.array([data['TopRightLongitude'],data['BottomRightLongitude']])-data['TopLeftLongitude']
        out=solve(m,n)
        trans[0,1],trans[0,2]=out[0],out[1]

        m=np.array([[data['WidthInPixels'], 0], [data['WidthInPixels'] ,data['HeightInPixels']]])
        n=np.array([data['TopRightLatitude'],data['BottomRightLatitude']])-data['TopLeftLatitude']
        print(m,n,data['TopLeftLatitude'])
        out=solve(m,n)
        trans[1,1],trans[1,2]=out[0],out[1]

        return trans
plgs =[SetTrans]