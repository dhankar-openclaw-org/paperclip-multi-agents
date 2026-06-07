import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/dhankar/temp/26_07__1/rfl__5_30/ros2_ws/install/robot_demo'
