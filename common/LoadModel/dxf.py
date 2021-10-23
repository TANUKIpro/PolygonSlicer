import sys
import logging
from math import floor

import numpy as np
import dxfgrabber

## log出力の設定
logging.basicConfig(level=logging.DEBUG)
dxf_logger = logging.getLogger(__name__)

class DXF_Loader:
    def __init__(self, file_extensor, extensor_reduced_scale, x_vias, y_vias, z_vias, inversion=1, integer=False):
        self.file_extensor = file_extensor
        self.reduced_scale = extensor_reduced_scale
        self.x_vias = x_vias#-100
        self.y_vias = y_vias#880
        self.z_vias = z_vias
        self.inversion = inversion  ## 反転操作(-1or1)
        self.round_quality = 5

        self.stop_points = []      ## 固定パーティクルの座標が格納
        self.poly_lines = []       ## ポリラインの頂点座標が格納
        self.particle_points = []  ## パーティクルの座標が格納
        self.integer = integer

        self.load_dxf()

    def show_data(self):
        print("ReduceScale={0}\nVias x={1}, y={2}, z={3}".format(self.reduced_scale, self.x_vias, self.y_vias, self.z_vias))

    def get_unique_list(self, seq):
        seen=[];return [x for x in seq if x not in seen and not seen.append(x)]
    
    ## データがそれっぽく見えるように整形(要修正！)
    def inThatWay(self, n, data_x, data_y, flag_integer):
        if flag_integer:
            x = int(data_x * self.reduced_scale + self.x_vias)
            y = int(data_y * self.reduced_scale * self.inversion + self.y_vias)
        else:
            x = floor((data_x * self.reduced_scale + self.x_vias)*10**n) / (10**n)
            y = floor((data_y * self.reduced_scale * self.inversion + self.y_vias)*10**n) / (10**n)
            x, y = round(x, self.round_quality), round(y, self.round_quality)
        return (x, y)

    def load_dxf(self):
        dxf = dxfgrabber.readfile(self.file_extensor)
        for i, layer in enumerate(dxf.layers):
            #print("Layer {0} : {1}".format(i, layer.name))
            dxf_logger.info("Layer {0} : {1}".format(i, layer.name))

        all_stop_points_en      = [e for e in dxf.entities if e.layer == 'stop_points']     ##  only CIRCLE
        all_polly_lines_en      = [e for e in dxf.entities if e.layer == 'polly_lines']     ##  only LWPOLYLINE
        all_particle_points_en  = [e for e in dxf.entities if e.layer == 'particle_points'] ##  only CIRCLE

        for sp_circle in all_stop_points_en:
            x, y = self.inThatWay(12, sp_circle.center[0], sp_circle.center[1], self.integer)
            self.stop_points.append([x, y])

        for lw_polyline in all_polly_lines_en:
            lump = []
            for cood in lw_polyline.points:
                x, y = self.inThatWay(12, cood[0], cood[1], self.integer)
                lump.append([x, y])
            self.poly_lines.append(lump)

        for circle in all_particle_points_en:
            x, y = self.inThatWay(12, circle.center[0], circle.center[1], self.integer)
            self.particle_points.append([x, y])

        dxf_logger.info("Clearing duplicate particles : {0} --> {1}".format(len(self.particle_points),
        len(self.get_unique_list(self.particle_points))))
        self.particle_points = self.get_unique_list(self.particle_points)

    def load_names_list(self, dxf_names):
        dxf = dxfgrabber.readfile(dxf_names)
        for i, layer in enumerate(dxf.layers):
            #print("Layer {0} : {1}".format(i, layer.name))
            dxf_logger.info("Layer {0} : {1}".format(i, layer.name))

        extensor_digitorum_tendon_polly = [e for e in dxf.entities if e.layer == 'extensor_digitorum_tendon_polly']     ##  指伸筋腱
        #interosseus_tendon_R_polly      = [e for e in dxf.entities if e.layer == 'interosseus_tendon_R_polly']          ##  骨間筋腱_R
        #interosseus_tendon_L_polly      = [e for e in dxf.entities if e.layer == 'interosseus_tendon_L_polly']          ##  骨間筋腱_L
        #triangular_ligament_polly       = [e for e in dxf.entities if e.layer == 'triangular_ligament_polly']           ##  三角靭帯

        #edt, it_R, it_L, tl = [], [], [], []
        #for cood in extensor_digitorum_tendon_polly[0]:
        #    x, y = self.inThatWay(12, cood[0].points, cood[1].points, self.integer)
        #    edt.append([x, y])
        #return edt

    def ver_col_ind(self):
        """  2次元座標 --> 3次元座標　へ変換  """
        stop_points_2d = np.array(self.stop_points)
        stop_points_3d = np.zeros((stop_points_2d.shape[0], 3))+self.z_vias
        stop_points_3d[:,0]=stop_points_2d[:,0]
        stop_points_3d[:,1]=stop_points_2d[:,1]

        particle_points_2d = np.array(self.particle_points)
        particle_points_3d = np.zeros((particle_points_2d.shape[0], 3))+self.z_vias
        particle_points_3d[:,0]=particle_points_2d[:,0]
        particle_points_3d[:,1]=particle_points_2d[:,1]
        
        poly_lines_3d = []
        for line_clump in self.poly_lines:
            line_clump = np.array(line_clump)
            z_zeros = np.zeros((line_clump.shape[0], 1))+self.z_vias
            poly_lines_3d.append(np.hstack((line_clump, z_zeros)))

        return stop_points_3d, particle_points_3d, poly_lines_3d

    def color(self, ver, _r=1, _g=1, _b=1):
        col = np.zeros_like(ver).tolist()
        for i, _ in enumerate(col):
            amari = i%3
            if   amari == 0:
                col[i] = _r
            elif amari == 1:
                col[i] = _g
            elif amari == 2:
                col[i] = _b
        return col
