#!/bin/bash

# ============================================================

# TURTLEBOT3 + GAZEBO + SLAM TOOLBOX + RVIZ

# SELF-HEALING LAUNCHER

#

# ROS2 Humble

# TurtleBot3 Waffle Pi

# Cyclone DDS

#

# Features:

# - Kills stale Gazebo processes

# - Kills stale SLAM processes

# - Kills stale ROS2 daemon

# - Verifies Gazebo spawn service

# - Starts Gazebo

# - Starts SLAM Toolbox

# - Starts RViz

# - Starts Diagnostics Terminal

# ============================================================

set -e

echo
echo "======================================"
echo "TURTLEBOT3 SELF-HEALING SLAM LAUNCHER"
echo "======================================"
echo

#

# ----------------------------------------------------------

# CLEANUP SECTION

# ----------------------------------------------------------

#

echo "[1/8] Killing stale ROS/Gazebo processes..."

pkill -9 -f gzserver 2>/dev/null || true
pkill -9 -f gzclient 2>/dev/null || true
pkill -9 -f spawn_entity.py 2>/dev/null || true
pkill -9 -f robot_state_publisher 2>/dev/null || true
pkill -9 -f slam_toolbox 2>/dev/null || true
pkill -9 -f async_slam_toolbox_node 2>/dev/null || true
pkill -9 -f turtlebot3_diff_drive 2>/dev/null || true
pkill -9 -f turtlebot3_laserscan 2>/dev/null || true

sleep 2

echo "[2/8] Stopping ROS daemon..."

source /opt/ros/humble/setup.bash

ros2 daemon stop 2>/dev/null || true

pkill -9 -f ros2cli.daemon 2>/dev/null || true

sleep 2

echo "[3/8] Resetting ROS environment..."

unset ROS_DOMAIN_ID
unset ROS_LOCALHOST_ONLY


export TURTLEBOT3_MODEL=waffle_pi

echo
echo "ROS Environment:"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
echo "TURTLEBOT3_MODEL=$TURTLEBOT3_MODEL"
echo


# ----------------------------------------------------------

# CLEAN ROS ENVIRONMENT

# ----------------------------------------------------------

unset ROS_DOMAIN_ID
unset ROS_LOCALHOST_ONLY
unset RMW_IMPLEMENTATION

source /opt/ros/humble/setup.bash

export TURTLEBOT3_MODEL=waffle_pi

echo
echo "ROS Environment:"
echo "ROS_DISTRO=$ROS_DISTRO"
echo "TURTLEBOT3_MODEL=$TURTLEBOT3_MODEL"
echo



#

# ----------------------------------------------------------

# GAZEBO

# ----------------------------------------------------------

#



echo "[4/8] Starting Gazebo..."

# This first launch creates the base window configuration container
gnome-terminal --window --title="TB3-GAZEBO" -- bash -c '
unset ROS_DOMAIN_ID
unset ROS_LOCALHOST_ONLY
unset RMW_IMPLEMENTATION

source /opt/ros/humble/setup.bash

export TURTLEBOT3_MODEL=waffle_pi

echo
echo "======================================"
echo "GAZEBO TERMINAL"
echo "======================================"

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

exec bash
'





#

# Wait for Gazebo

#

echo
echo "Waiting for Gazebo startup..."
echo

FOUND=0
for i in {1..90}
do
    if ros2 topic list 2>/dev/null | grep -q "/scan"
    then
        FOUND=1
        break
    fi

    sleep 1
    echo "Waiting for TurtleBot sensors... $i"
done



if [ $FOUND -eq 0 ]
then
echo
echo "ERROR:"
echo "/spawn_entity never appeared."
echo
echo "Gazebo failed to initialize."
echo
exit 1
fi

echo
echo "SUCCESS: /spawn_entity discovered"
echo


if [ $FOUND -eq 0 ]
then
    echo
    echo "ERROR:"
    echo "TurtleBot sensor topic /scan never appeared."
    echo

    echo "Current topics:"
    ros2 topic list || true

    echo
    echo "Current nodes:"
    ros2 node list || true

    exit 1
fi

#

# ----------------------------------------------------------

# SLAM TOOLBOX

# ----------------------------------------------------------

#

echo "[5/8] Starting SLAM Toolbox..."


# Swapped out to inject directly as a Tab entry layer
gnome-terminal --tab --title="TB3-SLAM" -- bash -c '
unset ROS_DOMAIN_ID
unset ROS_LOCALHOST_ONLY
unset RMW_IMPLEMENTATION

source /opt/ros/humble/setup.bash

echo
echo "======================================"
echo "SLAM TOOLBOX TERMINAL"
echo "======================================"

ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true

exec bash
'


sleep 8

#

# ----------------------------------------------------------

# RVIZ

# ----------------------------------------------------------

#

echo "[6/8] Starting RViz..."

# Swapped out to inject directly as a Tab entry layer
gnome-terminal --tab --title="TB3-RVIZ" -- bash -c '
source /opt/ros/humble/setup.bash

unset ROS_DOMAIN_ID
unset ROS_LOCALHOST_ONLY



echo
echo "======================================"
echo "RVIZ TERMINAL"
echo "======================================"
echo

rviz2

exec bash
'

sleep 3

#

# ----------------------------------------------------------

# DIAGNOSTICS

# ----------------------------------------------------------

#



echo "[7/8] Starting Diagnostics..."

# Swapped out to inject directly as a Tab entry layer
gnome-terminal --tab --title="TB3-DIAGNOSTICS" -- bash -c '
source /opt/ros/humble/setup.bash

unset ROS_DOMAIN_ID
unset ROS_LOCALHOST_ONLY


echo
echo "======================================"
echo "ROS2 DIAGNOSTICS"
echo "======================================"
echo

echo "NODES"
echo "--------------------------------------"
ros2 node list

echo
echo "TOPICS"
echo "--------------------------------------"
ros2 topic list

echo
echo "SERVICES"
echo "--------------------------------------"
ros2 service list | grep spawn

echo
echo "SCAN INFO"
echo "--------------------------------------"
ros2 topic info /scan

echo
echo "MAP INFO"
echo "--------------------------------------"
ros2 topic info /map

echo
echo
echo "Useful Commands:"
echo
echo "ros2 topic hz /scan"
echo "ros2 topic echo /map --once"
echo "ros2 run tf2_ros tf2_echo map odom"
echo

exec bash
'

#

# ----------------------------------------------------------

# HEALTH CHECK

# ----------------------------------------------------------

#

echo "[8/8] Final Health Check..."

sleep 10

echo
echo "======================================"
echo "FINAL STATUS"
echo "======================================"
echo

echo "Nodes:"
ros2 node list 2>/dev/null || true

echo
echo "Spawn Service:"
ros2 service list 2>/dev/null | grep spawn || true

echo
echo "Scan Topic:"
ros2 topic list 2>/dev/null | grep scan || true

echo
echo "Map Topic:"
ros2 topic list 2>/dev/null | grep map || true

echo
echo "======================================"
echo "LAUNCH COMPLETE"
echo "======================================"
echo
echo "Move the TurtleBot in Gazebo."
echo "Watch RViz for map creation."
echo
echo "If map remains empty:"
echo "  ros2 topic echo /map --once"
echo "  ros2 run tf2_ros tf2_echo map odom"
echo