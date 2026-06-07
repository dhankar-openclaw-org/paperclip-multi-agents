from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'robot_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),


    # data_files=[
    #     ('share/ament_index/resource_index/packages',
    #         ['resource/' + package_name]),
    #     ('share/' + package_name, ['package.xml']),
    # ],
    
    data_files=[
    (
        'share/ament_index/resource_index/packages',
        ['resource/' + package_name]
    ),
    (
        'share/' + package_name,
        ['package.xml']
    ),
    (
        os.path.join('share', package_name, 'launch'),
        glob('launch/*.py') ## Files --/ros2_ws/src/robot_demo/robot_demo/launch/launch_see_saw_world.py
    ),
    ],
    
    
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dhankar',
    maintainer_email='dhankar.rohit@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'hello_node = robot_demo.hello_node:main',
    ],
},
)
