"""
cd /home/dhankar/temp/26_07__1/rfl__5_30/

python3 -m venv --system-site-packages venv_ros_1
source /home/dhankar/temp/26_07__1/rfl__5_30/venv_ros_1/bin/activate

"""


#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

class TurtleBotVideoRecorder(Node):
    def __init__(self):
        super().__init__('turtlebot_video_recorder')
        
        # 1. Instantiate the ROS-OpenCV bridge converter
        self.bridge = CvBridge()
        
        # 2. Define the topic name.
        # Note: If your Turtlebot uses a different namespace, change this to match your topic.
        # You can verify yours by running: ros2 topic list | grep image
        self.image_topic = '/camera/image_raw' 
        
        # 3. Create Subscription to the camera topic
        self.subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10  # Queue size
        )
        
        # 4. Video Recording Configurations
        self.output_filename = 'turtlebot_simulation.mp4'
        self.fps = 20.0  # Typical frames per second from Gazebo simulation cameras
        self.video_writer = None  # Instantiated dynamically once first frame arrives
        
        self.get_logger().info(f"Video Recorder Initialized. Listening to: {self.image_topic}")
        self.get_logger().info("Waiting for first camera frame...")

    def image_callback(self, msg):
        try:
            # Convert ROS 2 Image message into an OpenCV standard BGR image array
            cv_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Dynamically initialize VideoWriter using frame height & width on arrival
            if self.video_writer is None:
                height, width, channels = cv_frame.shape
                
                # Define MP4 container video codec
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                
                self.video_writer = cv2.VideoWriter(
                    self.output_filename, 
                    fourcc, 
                    self.fps, 
                    (width, height)
                )
                self.get_logger().info(f"Started Recording: {width}x{height} resolution at {self.fps} FPS.")
                self.get_logger().info(f"Saving output file to: {os.path.abspath(self.output_filename)}")

            # Write current viewport matrix frame into MP4 file container
            self.video_writer.write(cv_frame)
            
            # Render frame stream to a popup desktop UI window
            cv2.imshow("TurtleBot Live Viewport", cv_frame)
            
            # Listen for user escape key configurations ('q' to exit safely)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.get_logger().info("User pressed 'q'. Exiting recording sequence...")
                self.shutdown_node_safely()

        except Exception as e:
            self.get_logger().error(f"Failed to process image frame: {str(e)}")

    def shutdown_node_safely(self):
        """Releases heavy rendering hooks to prevent video stream corruption."""
        if self.video_writer is not None:
            self.video_writer.release()
            self.get_logger().info("Video file compiled and closed cleanly.")
        cv2.destroyAllWindows()
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = TurtleBotVideoRecorder()
    
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        node.get_logger().info("Keyboard Interrupt detected.")
    finally:
        # Check if rclpy is still active to avoid multi-destruction errors
        if rclpy.ok():
            node.shutdown_node_safely()

if __name__ == '__main__':
    main()