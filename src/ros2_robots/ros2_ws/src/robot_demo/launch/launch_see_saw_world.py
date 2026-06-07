from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():

    return LaunchDescription([
        ExecuteProcess(
            cmd=[
                'gazebo',
                '--verbose',
                '/usr/share/gazebo-11/worlds/seesaw.world'
            ],
            output='screen'
        )
    ])