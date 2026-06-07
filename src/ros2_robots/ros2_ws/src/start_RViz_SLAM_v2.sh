#!/bin/bash

source /opt/ros/humble/setup.bash

mkdir -p ~/rviz

cat > ~/rviz/slam.rviz <<'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays

Visualization Manager:

  Global Options:
    Fixed Frame: odom

  Displays:

    - Class: rviz_default_plugins/Grid
      Name: Grid

    - Class: rviz_default_plugins/TF
      Name: TF

    - Class: rviz_default_plugins/LaserScan
      Name: LaserScan
      Topic:
        Value: /scan
      Reliability Policy: Best Effort
      Durability Policy: Volatile
      History Policy: Keep Last
      Depth: 5

    - Class: rviz_default_plugins/RobotModel
      Name: RobotModel
      Description Topic:
        Value: /robot_description

    - Class: rviz_default_plugins/Map
      Name: Map
      Topic:
        Value: /map
      Reliability Policy: Reliable
      Durability Policy: Transient Local

    - Class: rviz_default_plugins/Odometry
      Name: Odometry
      Topic:
        Value: /odom
EOF

rviz2 -d ~/rviz/slam.rviz --ros-args -p use_sim_time:=true