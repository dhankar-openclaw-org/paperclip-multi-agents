import math
import time

import rclpy

from gazebo_msgs.srv import DeleteEntity
from gazebo_msgs.srv import SpawnEntity


SPHERE_FILE = (
    "/home/dhankar/temp/26_07__1/rfl__5_30/"
    "ros2_ws/custom_models/sphere.sdf"
)



# name, radius, angular_speed

SPHERES = [

    ("sphere_01", 2.0, 1.00),
    ("sphere_02", 3.0, 0.95),
    ("sphere_03", 4.0, 0.90),
    ("sphere_04", 5.0, 0.85),
    ("sphere_05", 6.0, 0.80),

    ("sphere_06", 7.0, 0.75),
    ("sphere_07", 8.0, 0.70),
    ("sphere_08", 9.0, 0.65),
    ("sphere_09", 10.0, 0.60),
    ("sphere_10", 11.0, 0.55),

]


def delete_entity(node, client, name):

    req = DeleteEntity.Request()
    req.name = name

    future = client.call_async(req)

    rclpy.spin_until_future_complete(
        node,
        future
    )


def spawn_entity(
    node,
    client,
    name,
    x,
    y,
    z
):

    req = SpawnEntity.Request()

    req.name = name

    with open(
        SPHERE_FILE,
        "r"
    ) as f:

        req.xml = f.read()

    req.initial_pose.position.x = float(x)
    req.initial_pose.position.y = float(y)
    req.initial_pose.position.z = float(z)

    future = client.call_async(req)

    rclpy.spin_until_future_complete(
        node,
        future
    )


def main():

    rclpy.init()

    node = rclpy.create_node(
        "ten_spheres"
    )

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

    t = 0.0

    dt = 0.02

    while True:

        for index, (
            name,
            radius,
            speed
        ) in enumerate(SPHERES):

            phase = (
                index
                * 2.0
                * math.pi
                / len(SPHERES)
            )

            angle = (
                speed * t
            ) + phase

            x = (
                radius
                * math.cos(angle)
            )

            y = (
                radius
                * math.sin(angle)
            )

            try:
                delete_entity(
                    node,
                    delete_client,
                    name
                )
            except:
                pass

            spawn_entity(
                node,
                spawn_client,
                name,
                x,
                y,
                2.0
            )

        t += dt

        time.sleep(0.05)


if __name__ == "__main__":
    main()






# SPHERES = [
#     ("sphere_1", 2.0, 1.0),
#     ("sphere_2", 4.0, 0.8),
#     ("sphere_3", 6.0, 0.6),
#     ("sphere_4", 8.0, 0.4),
#     ("sphere_5", 10.0, 0.2),
# ]


# def delete_entity(node, client, name):

#     req = DeleteEntity.Request()
#     req.name = name

#     future = client.call_async(req)

#     rclpy.spin_until_future_complete(
#         node,
#         future
#     )


# def spawn_entity(
#     node,
#     client,
#     name,
#     x,
#     y,
#     z
# ):

#     req = SpawnEntity.Request()

#     req.name = name

#     with open(
#         SPHERE_FILE,
#         "r"
#     ) as f:

#         req.xml = f.read()

#     req.initial_pose.position.x = float(x)
#     req.initial_pose.position.y = float(y)
#     req.initial_pose.position.z = float(z)

#     future = client.call_async(req)

#     rclpy.spin_until_future_complete(
#         node,
#         future
#     )


# def main():

#     rclpy.init()

#     node = rclpy.create_node(
#         "five_spheres"
#     )

#     spawn_client = node.create_client(
#         SpawnEntity,
#         "/spawn_entity"
#     )

#     delete_client = node.create_client(
#         DeleteEntity,
#         "/delete_entity"
#     )

#     spawn_client.wait_for_service()
#     delete_client.wait_for_service()

#     t = 0.0

#     while True:

#         for name, radius, speed in SPHERES:

#             try:
#                 delete_entity(
#                     node,
#                     delete_client,
#                     name
#                 )
#             except:
#                 pass

#             angle = t * speed

#             x = radius * math.cos(angle)

#             y = radius * math.sin(angle)

#             spawn_entity(
#                 node,
#                 spawn_client,
#                 name,
#                 x,
#                 y,
#                 2.0
#             )

#         t += 0.1

#         time.sleep(0.2)


# if __name__ == "__main__":
#     main()
