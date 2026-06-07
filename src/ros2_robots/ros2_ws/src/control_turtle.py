
###/home/dhankar/temp/26_07__1/rfl__5_30/ros2_ws/src/control_turtle.py
## cd /home/dhankar/temp/26_07__1/rfl__5_30/ros2_ws/src/
## python3 control_turtle.py


#!/usr/bin/env python3
import threading
import sys
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist  # <--- Added for driving
import math

class LidarAndMotionControlNode(Node):
    def __init__(self):
        super().__init__('lidar_control_node')
        
        # 1. State Variables for Terminal Controls
        self.display_mode = 'front'  
        self.safe_threshold = 0.5    
        
        # 2. Setup QoS Profile matching typical Gazebo Lidar sensors
        sensor_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10
        )
        
        # 3. Create Subscriber to standard /scan topic
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            qos_profile=sensor_qos
        )

        # 4. Create Publisher to command velocity topic to drive the bot
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        self.get_logger().info("Lidar & Motion Controller Node Initialized.")

    def send_drive_command(self, linear_x, angular_z):
        """Helper function to compile and publish movement coordinates."""
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        self.cmd_vel_pub.publish(msg)

    def lidar_callback(self, msg):
        """Processes live lidar sensor arrays from Gazebo."""
        if self.display_mode == 'none':
            return

        ranges = msg.ranges
        num_readings = len(ranges)
        
        if num_readings == 0:
            return

        clean_ranges = [r if (not math.isinf(r) and not math.isnan(r)) else msg.range_max for r in ranges]
        min_dist = min(clean_ranges)
        
        if self.display_mode == 'summary':
            print(f"\r[SUMMARY] Total Rays: {num_readings} | Min Distance: {min_dist:.2f}m", end="", flush=True)
            
        elif self.display_mode == 'front':
            front_index = 0
            front_dist = clean_ranges[front_index]
            alert = "⚠️  TOO CLOSE!" if front_dist < self.safe_threshold else "✅ CLEAR"
            print(f"\r[FRONT RADAR] Distance: {front_dist:.2f}m | Status: {alert}", end="", flush=True)
            
        elif self.display_mode == 'all':
            quarter = num_readings // 4
            front = clean_ranges[0]
            left = clean_ranges[quarter]
            rear = clean_ranges[quarter * 2]
            right = clean_ranges[quarter * 3]
            print(f"\r[ALL ZONES] F: {front:.2f}m | L: {left:.2f}m | B: {rear:.2f}m | R: {right:.2f}m", end="", flush=True)


def terminal_control_loop(node):
    """Runs a dedicated thread to capture command-line instructions and drive inputs."""
    print("\n" + "="*50)
    print(" LIVE TELEMETRY & TURTLEBOT MOTION CONTROLS")
    print("="*50)
    print(" Driving Controls:")
    print("  w - Forward   |  s - Stop  |  x - Backward")
    print("  a - Turn Left |  d - Turn Right")
    print("\n Data View Settings:")
    print("  mode [front / all / summary / none]")
    print("  set [meters]  - Adjust collision threshold (e.g., 'set 0.8')")
    print("  quit          - Terminate node cleanly")
    print("="*50 + "\n")

    # Fixed movement increments
    linear_speed = 0.2   # m/s
    angular_speed = 0.5  # rad/s

    while rclpy.ok():
        try:
            user_input = input().strip().lower()
            if not user_input:
                continue
                
            parts = user_input.split()
            command = parts[0]
            
            # --- MOTION COMMAND PROCESSING ---
            if command == 'w':
                node.send_drive_command(linear_speed, 0.0)
                print("\n>> Executing: [FORWARD]")
            elif command == 'x':
                node.send_drive_command(-linear_speed, 0.0)
                print("\n>> Executing: [BACKWARD]")
            elif command == 'a':
                node.send_drive_command(0.0, angular_speed)
                print("\n>> Executing: [ROTATE LEFT]")
            elif command == 'd':
                node.send_drive_command(0.0, -angular_speed)
                print("\n>> Executing: [ROTATE RIGHT]")
            elif command == 's':
                node.send_drive_command(0.0, 0.0)
                print("\n>> Executing: [BRAKE / STOP]")
            
            # --- ORIGINAL SETTING COMMANDS ---
            elif command == 'quit':
                node.send_drive_command(0.0, 0.0) # Safety stop on exiting
                print("\nShutting down subscriber & publisher down...")
                break
            elif command == 'mode' and len(parts) > 1:
                target_mode = parts[1]
                if target_mode in ['front', 'all', 'summary', 'none']:
                    node.display_mode = target_mode
                    print(f"\n>> Switched terminal view to: [{target_mode.upper()}]")
                else:
                    print(f"\n❌ Unknown mode '{target_mode}'.")
            elif command == 'set' and len(parts) > 1:
                try:
                    val = float(parts[1])
                    node.safe_threshold = val
                    print(f"\n>> Set Safety Threshold to: {val}m")
                except ValueError:
                    print("\n❌ Invalid distance formatting.")
            else:
                print("\n❌ Command structure unrecognized. Use w, a, s, d, x to drive.")
        except (KeyboardInterrupt, EOFError):
            break


def main(args=None):
    rclpy.init(args=args)
    node = LidarAndMotionControlNode()

    input_thread = threading.Thread(target=terminal_control_loop, args=(node,), daemon=True)
    input_thread.start()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()



# #!/usr/bin/env python3
# import threading
# import sys
# import rclpy
# from rclpy.node import Node
# from rclpy.qos import QoSProfile, QoSReliabilityPolicy
# from sensor_msgs.msg import LaserScan
# import math

# class LidarControlNode(Node):
#     def __init__(self):
#         super().__init__('lidar_control_node')
        
#         # 1. State Variables for Terminal Controls
#         self.display_mode = 'front'  # Options: 'front', 'all', 'summary', 'none'
#         self.safe_threshold = 0.5    # Distance in meters for proximity alerts
        
#         # 2. Setup QoS Profile matching typical Gazebo Lidar sensors
#         sensor_qos = QoSProfile(
#             reliability=QoSReliabilityPolicy.BEST_EFFORT,
#             depth=10
#         )
        
#         # 3. Create Subscriber to standard /scan topic
#         self.subscription = self.create_subscription(
#             LaserScan,
#             '/scan',
#             self.lidar_callback,
#             qos_profile=sensor_qos
#         )
        
#         self.get_logger().info("Lidar Controller Node Initialized. Connected to /scan.")

#     def lidar_callback(self, msg):
#         """Processes live lidar sensor arrays from Gazebo."""
#         if self.display_mode == 'none':
#             return

#         ranges = msg.ranges
#         num_readings = len(ranges)
        
#         if num_readings == 0:
#             return

#         # Replace 'inf' or 'nan' values with max range for stable calculations
#         clean_ranges = [r if (not math.isinf(r) and not math.isnan(r)) else msg.range_max for r in ranges]
#         min_dist = min(clean_ranges)
        
#         # Handle the custom modes chosen by user terminal commands
#         if self.display_mode == 'summary':
#             print(f"\r[SUMMARY] Total Rays: {num_readings} | Min Distance Vector: {min_dist:.2f}m", end="", flush=True)
            
#         elif self.display_mode == 'front':
#             # Looking directly forward (usually array index 0 or split at the edges depending on lidar setup)
#             # For TurtleBot3, 0 degrees is the very first index.
#             front_index = 0
#             front_dist = clean_ranges[front_index]
            
#             alert = "⚠️  TOO CLOSE!" if front_dist < self.safe_threshold else "✅ CLEAR"
#             print(f"\r[FRONT RADAR] Distance: {front_dist:.2f}m | Status: {alert}", end="", flush=True)
            
#         elif self.display_mode == 'all':
#             # Split the lidar sweep into 4 zones (Front, Left, Rear, Right)
#             # Assuming a 360-degree LiDAR scanner (TurtleBot default)
#             quarter = num_readings // 4
#             front = clean_ranges[0]
#             left = clean_ranges[quarter]
#             rear = clean_ranges[quarter * 2]
#             right = clean_ranges[quarter * 3]
            
#             print(f"\r[ALL ZONES] F: {front:.2f}m | L: {left:.2f}m | B: {rear:.2f}m | R: {right:.2f}m", end="", flush=True)


# def terminal_control_loop(node):
#     """Runs a dedicated thread to capture command-line instructions on the fly."""
#     print("\n" + "="*50)
#     print(" LIVE LIDAR TERMINAL CONTROLS")
#     print("="*50)
#     print("Commands:")
#     print("  mode front    - Show only forward-facing radar sensor")
#     print("  mode all      - Cross-examine 4 quadrants (F, L, B, R)")
#     print("  mode summary  - Stream absolute closest proximity target")
#     print("  mode none     - Mute output stream")
#     print("  set [meters]  - Adjust collision threshold (e.g., 'set 0.8')")
#     print("  quit          - Terminate node cleanly")
#     print("="*50 + "\n")

#     while rclpy.ok():
#         try:
#             user_input = input().strip().lower()
#             if not user_input:
#                 continue
                
#             parts = user_input.split()
#             command = parts[0]
            
#             if command == 'quit':
#                 print("\nShutting down subscriber down...")
#                 break
                
#             elif command == 'mode' and len(parts) > 1:
#                 target_mode = parts[1]
#                 if target_mode in ['front', 'all', 'summary', 'none']:
#                     node.display_mode = target_mode
#                     print(f"\n>> Switched terminal view to: [{target_mode.upper()}]")
#                 else:
#                     print(f"\n❌ Unknown mode '{target_mode}'. Choose: front, all, summary, none")
                    
#             elif command == 'set' and len(parts) > 1:
#                 try:
#                     val = float(parts[1])
#                     node.safe_threshold = val
#                     print(f"\n>> Set Safety Threshold to: {val}m")
#                 except ValueError:
#                     print("\n❌ Invalid distance formatting. Use e.g. 'set 0.5'")
#             else:
#                 print("\n❌ Command structure unrecognized.")
#         except (KeyboardInterrupt, EOFError):
#             break


# def main(args=None):
#     rclpy.init(args=args)
#     node = LidarControlNode()

#     # Spin up terminal interaction loop in a background thread
#     input_thread = threading.Thread(target=terminal_control_loop, args=(node,), daemon=True)
#     input_thread.start()

#     try:
#         # Keep ROS 2 running to pick up callbacks
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()