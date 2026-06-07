# move_sphere.py

import rclpy

from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState


def main():

    rclpy.init()

    node = rclpy.create_node('move_sphere')

    client = node.create_client(
        SetEntityState,
        '/gazebo/set_entity_state'
    )

    client.wait_for_service()

    request = SetEntityState.Request()

    state = EntityState()

    state.name = 'sphere'

    state.pose.position.x = 3.0
    state.pose.position.y = 0.0
    state.pose.position.z = 1.0

    request.state = state

    future = client.call_async(request)

    rclpy.spin_until_future_complete(
        node,
        future
    )

    print("Sphere moved")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()