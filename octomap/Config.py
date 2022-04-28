import logging
import math

"""
The probability change for each new observation.
The default value is from the '5.1 Evaluation - Sensor model for laser range data' of the OctoMap Paper.
"""
HIT_LOGODDS=0.85
HIT_PROBABILITY=0.7    
MISS_LOGODDS=-0.4
MISS_PROBABILITY=0.4

"""
The probability threshold for occupany and free.
If there is not threshold, the status change will be very hard and not in time. 
When the probability of the voxel is arrived at the threshold, it indicates the voxel has been set occupied/free status.
"""
OCCUPANY_LOGODDS=3.5
OCCUPANY_PROBABILITY=0.97
FREE_LOGODDS=-2
FREE_PROBABILITY=0.12

"""
Initial probability value.
"""
DEFAULT_PROBABILITY=0.5
DEFAULT_LOGODDS=0

"""
Shape of the OctoTree, a cube with the same width, length and the height.
TREE_RESOLUTION (cm): the size of each voxel.
TREE_MAX_DEPTH: the recursion of the tree.
WIDTH: the width of the experimental scene.
So, the size of the OctoTree is TREE_RESOLUTION * 2^TREE_MAX_DEPTH.
"""
TREE_RESOLUTION=4
TREE_MAX_DEPTH=6
TREE_CENTER=(0, 0, 0)
WIDTH=TREE_RESOLUTION * math.pow(2, TREE_MAX_DEPTH)

"""
Crazyflie and its laser sensor.
"""
URI='radio://0/80/2M/E7E7E7E7E7'
SENSOR_TH=400
PLOT_SENSOR_DOWN=False
WHETHER_FLY=True

"""
Visualization.
The coornidate under the OctoTree should be adjusted to the Matplotlib.
Use offset to demonstrate the OctoMap in the center of Matplotlib Voxel.
"""
OFFSETX=math.pow(2, TREE_MAX_DEPTH) / 2
OFFSETY=math.pow(2, TREE_MAX_DEPTH) / 2
OFFSETZ=math.pow(2, TREE_MAX_DEPTH) / 2
INDICE_LENGTH= math.pow(2, TREE_MAX_DEPTH)

"""
Path Plan based on RRT.
GOAL_SAMPLE_RATE: the probability of picking the target point.
EXPAND_STEP: step size per growth.
SHOW_ANIMATION: animation effect for RRT algorithm display.
"""
GOAL_SAMPLE_RATE=0.05
EXPAND_STEP=2
SHOW_ANIMATION=True

"""
Global logger.
"""
# Only output errors from the logging framework
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()
