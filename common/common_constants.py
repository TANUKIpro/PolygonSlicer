## models path
import platform
if platform.system() == "Darwin":
    TO_MODEL    = "/Users/ryotaro/Desktop/grad_prj/data/model"
elif "Windows":
    TO_MODEL    = "C:/Users/ryota/Desktop/grad_prj/data/model"
FINGER      = "/Index"
TO_BONE     = TO_MODEL + FINGER + "/bone"
TO_EXTENSOR = TO_MODEL + FINGER + "/extensor"

## export path **(Counterpart)**
TO_CSV        = "../data/csv"
TO_CSV_INPUT  = TO_CSV + "/input"
TO_CSV_OUTPUT = TO_CSV + "/output"

## extensor
EXTENSOR_NAME = "/extensor_hood_test002.dxf"
## bone
BONE_NAMES    = ["/Metacarpal3_01.stl",
                 "/Proximal_Phalanx3_01_org.stl",
                 "/Middle_Phalanxh3_01_org.stl",
                 "/Distal_Phalanxh3_01_org.stl"]

## constants
EXTENSOR_REDUCE_SCALE = 1/1500
BONE_REDUCE_SCALE     = 1/15
#EXTENSOR_REDUCE_SCALE = 1/100
#BONE_REDUCE_SCALE     = 1

# 腱モデルの初期位置の調性
DXF_X_VIAS = -0.65
DXF_Y_VIAS = 2.
DXF_Z_VIAS = -1.5

# 腱モデルの各停止点のリスト
# 末節骨に停止している座標
"""
distal_phalanx_spp = [[2510, 12920],
                      [2660, 12920],
                      [2810, 12920]]
"""
distal_phalanx_spp = [[1.02333, 10.61333],
                      [1.12333, 10.61333],
                      [1.22333, 10.61333]]
#中節骨に停止している座標
"""
middle_phalanx_spp = [[2510, 10330],
                      [2660, 10330],
                      [2810, 10330]]
"""
middle_phalanx_spp = [[1.02333, 8.88667],
                      [1.12333, 8.88667],
                      [1.22333, 8.88667]]

# color
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
RED   = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE  = (0, 0, 1)

# in particle
COLLISION_NORM_THRESHOLD = 0.5

# in drawer
BYTE_SIZE = 4

# in dxf_loader
INT_PADDING = 12

# in main
DT       = 0.2
NUM_ITER = 30
GRAVITY  = 9.8

## core
WINDOW_TYTLE = "FINGER SIM@Qt5 with OpenGL v1.0.4"
SCREEN_W     = 600
SCREEN_H     = 500
SCREEN_SIZE  = [SCREEN_W, SCREEN_H]