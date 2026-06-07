#!/bin/bash

# =====================================================
# TurtleBot3 + Gazebo + SLAM + RViz Launcher
# ROS2 Humble
# =====================================================

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export TURTLEBOT3_MODEL=waffle_pi

ROS_SETUP="source /opt/ros/humble/setup.bash"

echo "==========================================="
echo "Starting TurtleBot3 SLAM Environment"
echo "==========================================="

#
# Terminal 1 : Gazebo + TurtleBot
#
gnome-terminal --title="TB3-GAZEBO" -- bash -c "
$ROS_SETUP

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export TURTLEBOT3_MODEL=waffle_pi

echo 'Starting Gazebo...'

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

exec bash
"

sleep 15

#
# Wait for Gazebo spawn service
#
echo "Waiting for /spawn_entity ..."

for i in {1..60}
do
    if ros2 service list 2>/dev/null | grep -q "/spawn_entity"
    then
        echo "Found /spawn_entity"
        break
    fi

    sleep 1
done

#
# Terminal 2 : SLAM Toolbox
#
gnome-terminal --title="TB3-SLAM" -- bash -c "
$ROS_SETUP

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo 'Starting SLAM Toolbox...'

ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true

exec bash
"

sleep 5

#
# Terminal 3 : RViz
#
gnome-terminal --title="TB3-RVIZ" -- bash -c "
$ROS_SETUP

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo 'Starting RViz...'

rviz2

exec bash
"

sleep 2

#
# Terminal 4 : Diagnostics
#
gnome-terminal --title="TB3-DIAGNOSTICS" -- bash -c "
$ROS_SETUP

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo
echo '========== ROS DIAGNOSTICS =========='
echo

echo 'Nodes:'
ros2 node list

echo
echo 'Topics:'
ros2 topic list

echo
echo 'TF Frames:'
ros2 topic list | grep tf

echo
echo 'Map Topics:'
ros2 topic list | grep map

echo
echo 'Laser Topics:'
ros2 topic list | grep scan

echo
echo 'Use these commands:'
echo 'ros2 topic hz /scan'
echo 'ros2 topic echo /map --once'
echo 'ros2 run tf2_ros tf2_echo map odom'

exec bash
"

echo
echo "==========================================="
echo "All terminals launched."
echo "==========================================="