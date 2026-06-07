import math
import time

import rclpy

from gazebo_msgs.srv import DeleteEntity
from gazebo_msgs.srv import SpawnEntity


SPHERE_FILE = "/home/dhankar/temp/26_07__1/rfl__5_30/ros2_ws/custom_models/sphere.sdf"
## /home/dhankar/temp/26_07__1/rfl__5_30/ros2_ws/custom_models/sphere.sdf

def spawn(client, x, y, z):

    req = SpawnEntity.Request()

    req.name = "sphere"

    req.xml = open(SPHERE_FILE).read()

    # req.initial_pose.position.x = x
    # req.initial_pose.position.y = y
    # req.initial_pose.position.z = z

    req.initial_pose.position.x = float(x)
    req.initial_pose.position.y = float(y)
    req.initial_pose.position.z = float(z)

    future = client.call_async(req)

    rclpy.spin_until_future_complete(node, future)


def delete(client):

    req = DeleteEntity.Request()

    req.name = "sphere"

    future = client.call_async(req)

    rclpy.spin_until_future_complete(node, future)


rclpy.init()

node = rclpy.create_node("move_sphere")

spawn_client = node.create_client(
    SpawnEntity,
    "/spawn_entity"
)



delete_client = node.create_client(
    DeleteEntity,
    "/delete_entity"
)

spawn_client.wait_for_service()
delete_client.wait_for_service()

t = 0

while True:

    try:
        delete(delete_client)
    except:
        pass

    x = 3 * math.cos(t)
    y = 3 * math.sin(t)

    # spawn(
    #     spawn_client,
    #     x,
    #     y,
    #     2
    # )

    spawn(
        spawn_client,
        float(x),
        float(y),
        2.0
        )

    t += 0.2

    time.sleep(0.5)