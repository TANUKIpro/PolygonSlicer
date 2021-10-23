import logging

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

if __package__==None:
    print("__package__==None && __name__==__main__")
    import sys
    sys.exit()
else:
    from . import common_constants as cc
    from . import drawer
    from .constraint import ParticleConstraint
    from .LoadModel import dxf
    from .particle import Particle

## log出力の設定
logging.basicConfig(level=logging.DEBUG)
extensor_logger = logging.getLogger(__name__)


class Extensor:
    def __init__(self, modelName):
        self.extensor_name = modelName
        self.path2extensor = cc.TO_EXTENSOR + self.extensor_name

        self.stop_points_3d     = None   # 固定パーティクルの座標
        self.particle_points_3d = None   # 可動パーティクルの座標
        self.poly_lines_3d      = None   # ポリラインの座標
        
        self.particles       = []        # 全パーティクルのインスタンス
        self.particle_normal = []        # 通常パーティクルのインスタンス
        self.particle_stop   = []        # 固定パーティクルのインスタンス
        self.disP_spp        = []        # 末節骨停止点のインスタンス
        self.midP_spp        = []        # 中節骨停止点のインスタンス
        self.other_spp       = []        # その他の停止点のインスタンス
        self.p_constraints   = []        # 全結束条件のインスタンス
    
    def load_dxf_model(self):
        extensor_logger.info("LOAD EXTENSOR MODEL")
        Extensor = dxf.DXF_Loader(self.path2extensor, cc.EXTENSOR_REDUCE_SCALE, cc.DXF_X_VIAS, cc.DXF_Y_VIAS, cc.DXF_Z_VIAS)
        self.stop_points_3d, self.particle_points_3d, self.poly_lines_3d = Extensor.ver_col_ind()
    
    ## 各パーティクルのインスタンスをセットアップ
    def setup_particle(self):
        # パーティクルのインスタンスを作成
        for p_point in self.particle_points_3d:
            p = Particle(p_point[0], p_point[1], p_point[2])
            self.particles.append(p)
        
        # 固定パーティクルを設定
        for sp in self.stop_points_3d:
            try:
                anc_idx = self.particle_points_3d.tolist().index(sp.tolist())
                self.particles[anc_idx].fixed = True
            except:
                extensor_logger.error("STOP POINT ERROR : {0}".format(sp))
        
        # ポリゴンラインの設定と一部の例外処理(要修正！)
        for pl in self.poly_lines_3d:
            pl = pl.tolist()
            for i in range(len(pl)-1):
                try:
                    if pl[i][1] == 5.8583:
                        index0 = 31
                    else:
                        index0 = self.particle_points_3d.tolist().index(pl[i])
                    if pl[i+1][1] == 5.8583:
                        index1 = 31
                    else:
                        index1 = self.particle_points_3d.tolist().index(pl[i+1])

                    c = ParticleConstraint(self.particles, index0, index1)
                    self.p_constraints.append(c)
                except:
                    extensor_logger.error("POLYGON LINE ERROR: [{0}, {1}]".format(pl[i], pl[i+1]))

        # 通常パーティクルと固定パーティクルを分類
        for i in range(len(self.particles)):
            if self.particles[i].fixed:
                self.particle_stop.append(self.particles[i])
            else:
                self.particle_normal.append(self.particles[i])

        # 固定パーティクルを更に末節骨停止点・中節骨停止点・その他に分類
        for spp in self.particle_stop:
            if spp.y == cc.distal_phalanx_spp[0][1]:
                self.disP_spp.append(spp)
            elif spp.y == cc.middle_phalanx_spp[0][1]:
                self.midP_spp.append(spp)
            else:
                self.other_spp.append(spp)

    ## パーティクルの位置、結束状態、衝突のアップデート
    def updatePP(self):
        for i in range(len(self.particles)):
            self.particles[i].update()

    def updateCONST(self):
        for _ in range(cc.NUM_ITER):
            for j in range(len(self.p_constraints)):
                self.p_constraints[j].update()
    
    def updateCOLLID(self, bone_mesh, threshold=cc.COLLISION_NORM_THRESHOLD):
        for i in range(len(self.particle_normal)):
            self.particle_normal[i].updateCollision(bone_mesh, threshold)

    def set_position(self, instance, pos):
        instance.set_pos(pos)
    
    def getPos(self, instance):
        return instance.x, instance.y, instance.z
    
    def drawDisP_StopParticle(self):
        #for i in range(len(self.disP_spp)):
        #    self.disP_spp[i].draw()
        self.disP_spp[0].draw()
        self.disP_spp[1].draw()
        self.disP_spp[2].draw()

    def drawMidP_StopParticle(self):
        #for i in range(len(self.midP_spp)):
        #    self.midP_spp[i].draw()
        self.midP_spp[0].draw()
        self.midP_spp[1].draw()
        self.midP_spp[2].draw()

    def drawOther_StopParticle(self):
        for i in range(len(self.other_spp)):
            self.other_spp[i].draw()

    ## 通常パーティクルの描画
    def drawNormalParticle(self):
        for i in range(len(self.particle_normal)):
            self.particle_normal[i].draw()
    
    ## 結束状態の描画
    def drawConstraint(self):
        for i in range(len(self.p_constraints)):
            self.p_constraints[i].draw()
