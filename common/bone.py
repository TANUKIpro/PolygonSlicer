import logging, sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

if __package__==None:
    print("__package__==None && __name__==__main__")
    import sys
    sys.exit()
else:
    from . import common_constants as cc
    from . import drawer
    from .LoadModel import stl

## log出力の設定
logging.basicConfig(level=logging.DEBUG)
bone_logger = logging.getLogger(__name__)


class Bone:
    def __init__(self, modelName):
        self.bone_name = modelName
        self.toBone = cc.TO_BONE + self.bone_name

        self.stl_instance = None
        self.bone_ver, self.bone_col, self.bone_ind = None, None, None
        self.bone_Frame_col = None
        self.init_buffers, self.buffers           = None, None
        self.init_wire_buffers, self.wire_buffers = None, None
        
        self.load_stl_model(self.toBone)

    ## stlモデルのロード
    def load_stl_model(self, path):
        ## STL_loaderからモデルの情報を持ったインスタンスを生成
        self.stl_instance = stl.STL_loader(path, cc.BONE_REDUCE_SCALE)
        ## モデルのstlデータからvboへ登録するためのデータを抽出
        self.bone_ver, self.bone_col, self.bone_ind = self.stl_instance.ver_col_ind()
        ## 輪郭用のワイヤーフレームの設定(color)
        self.bone_Frame_col = self.stl_instance.color(self.bone_ver, _r=0, _g=0, _b=0)

    ## モデルの頂点座標を軸に対して平行移動させる関数
    def moveParallelPos(self, vertices, vas_x, vas_y, vas_z):
        buff_x, buff_y, buff_z = vertices[0::3], vertices[1::3] ,vertices[2::3]
        vertices[0::3] = list(map(lambda ver_x:ver_x+vas_x, buff_x))
        vertices[1::3] = list(map(lambda ver_y:ver_y+vas_x, buff_y))
        vertices[2::3] = list(map(lambda ver_z:ver_z+vas_z, buff_z))
        
        drawer.moveVer(np.array(vertices, dtype=np.float32),
                       np.array(self.bone_col, dtype=np.float32),
                       np.array(self.bone_ind, dtype=np.float32))
    
    # データをvboへ登録
    def sub_vbo(self):
        bone_logger.info("subscribe to VBO :: {0}".format(self.bone_name))
        self.buffers      = drawer.create_vbo(self.init_buffers, self.bone_ver, self.bone_col, self.bone_ind)
        self.wire_buffers = drawer.create_vbo(self.init_wire_buffers, self.bone_ver, self.bone_Frame_col, self.bone_ind)
    
    # 登録したvboを描画
    def draw(self):
        drawer.draw_vbo(self.buffers,      self.bone_ind)
        drawer.draw_vbo(self.wire_buffers, self.bone_ind, mode_front=GL_LINE)
    
    # 指定軸に対するパーティクルの最大値を取得
    def getMaxCoordination(self, axis=1):
        max_index = np.argmax(np.array(self.stl_instance.all_mesh_particle)[:,axis])
        max_cood = self.stl_instance.all_mesh_particle[max_index]
        return max_cood