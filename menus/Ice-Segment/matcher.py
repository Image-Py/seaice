# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 03:48:49 2017

@author: yxl
"""

#import cv2
import numpy as np
from numpy.linalg import norm
from skimage.feature import (match_descriptors, corner_harris,
                             corner_peaks, ORB, plot_matches)

class Matcher:
    def __init__(self, dim , std):
        self.dim, self.std = dim, std
        self.V = np.mat(np.zeros((self.dim,1)))
        self.Dk = np.mat(np.diag(np.ones(self.dim)*1e6))
        
    def match(self, desc1, desc2):
        pair = match_descriptors(desc1, desc2, cross_check=True)
        lt = [((desc1[i[0]]^desc2[i[1]]).sum(), i[0], i[1]) for i in pair]

        return np.array(sorted(lt))[:,1:].astype(np.int16)

    def getT(self, v1, v2):
        (x1, y1), (x2, y2) = v1, v2
        if self.dim==6:
            return np.mat([[v1[0],v1[1],1,0,0,0],
                       [0,0,0,v1[0],v1[1],1]])
        if self.dim==8:
            return np.mat([[x1, y1, 1, 0, 0, 0, -x1*x2, -y1*x2],
                           [0, 0, 0, x1, y1, 1, -x1*y2, -y1*y2]])

    def test(self, v1, v2):
        T = self.getT(v1.A1,v2.A1)
        goal = T * self.V
        o = goal.reshape((1,2))
        d = norm(v2 - o)
        dv = (v2 - o)/d
        D = T * self.Dk * T.T
        s = np.sqrt(dv * D * dv.T + self.std ** 2)
        return 3 * s > d

    def accept(self, v1, v2):
        L = v2
        Dl = np.mat(np.diag(np.ones(2)))*self.std**2
        T = self.getT(v1.A1,v2.A1)
        CX = (self.Dk.I + T.T * Dl.I * T).I
        CL = CX * T .T* Dl.I
        CV = np.mat(np.diag(np.ones(self.dim))) - CX * T.T * Dl.I * T
        self.V = CL * L + CV * self.V
        self.Dk = CV * self.Dk * CV.T + CL * Dl * CL.T
        
    def normalrize(self, pts):
        o = pts.mean(axis=0)
        l = norm(pts-o, axis=1).mean()
        pts = (pts-o)/l
        return pts, np.mat([[1/l, 0, -o[0]/l],[0, 1/l, -o[1]/l],[0,0,1]])
        
    def filter(self, kpt1, feat1, kpt2, feat2):
        #kpt1 = np.array([(k.pt[0],k.pt[1]) for k in kpt1])
        #kpt2 = np.array([(k.pt[0],k.pt[1]) for k in kpt2])
        kpt1, self.m1 = self.normalrize(kpt1)
        kpt2, self.m2 = self.normalrize(kpt2)
        idx = self.match(feat1, feat2)
        if self.dim == 0: 
            return idx, np.ones(len(idx), dtype=np.bool), 1
        mask = []
        for i1, i2 in idx:
            v1 = np.mat(kpt1[i1])
            v2 = np.mat(kpt2[i2])
            if self.test(v1, v2):
                self.accept(v1.T,v2.T)
                mask.append(True)
            else: mask.append(False)
        mask = np.array(mask)
        #print mask
        return idx, mask, self.V

    def get_trans(self):
        result = np.eye(3)
        result[:2] = self.V.reshape((2,3))
        return result

    def check_v(self):
        trans = self.getTrans()[:2,:2]
        axis = norm(trans,axis=0)
        return norm(axis-1)< 0.5

    def get_ori_trans(self, k):
        mk = np.mat([[k,0,0],[0,k,0],[0,0,1]])
        self.get_trans()
        rst = mk.I * self.m2.I * self.get_trans() * self.m1 * mk
        return rst
        # !K * !M2 * T2 * M1 * K