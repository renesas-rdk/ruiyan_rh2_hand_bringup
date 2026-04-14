# ruiyan_rh2_hand_bringup

ROS 2 package that provides launch files, controller configurations, robot descriptions, and test scripts for the Ruiyan RH2 6-DOF dexterous hand. This package contains everything needed to bring up and operate the hand.

## Features
- Launch files for different control modes (joint position, joint trajectory)
- Controller configurations for all supported control modes
- Complete hand URDF descriptions (left and right hand configurations)
- Test scripts for validating hand functionality
- Foxglove Studio configuration for visualization

**Note:** Before using the RuiYan RH2 Dexhand, ensure that the hand is properly initialized using the provided setup script located in the ``ruiyan_rh2_hand_bringup/setup/ruiyan_rh2_init.sh`` or in the ``install/ruiyan_rh2_hand_bringup/share/ruiyan_rh2_hand_bringup/setup/ruiyan_rh2_init.sh`` after installation.

## Related Packages
- **ruiyan_rh2_hand_ros2_control**: Contains the hardware interface implementation
- **ruiyan_rh2_hand_description**: Contains the hand's visual and collision meshes, joint definitions

## Package layout
- `launch/`: Launch files for different control modes
- `setup/`: Setup scripts for configuring the CAN interface
- `config/`: Controller and controller_manager YAML configurations
- `urdf/`: Complete hand URDF descriptions (left and right)
- `test/`: Example scripts for testing hand functionality

## Prerequisites
- ROS 2 (Jazzy or newer) with `ros2_control` and `ros2_controllers` ecosystem
- A colcon workspace (e.g., `~/ros2_ws`)
- `ruiyan_rh2_hand_ros2_control` package for hardware interface
- `ruiyan_rh2_hand_description` package for hand description

## Launch Modes

### Run the setup script
If you are using a physical Ruiyan RH2 hand, run the setup script to configure the CAN interface:
```bash
cd ~/ros2_ws
./install/ruiyan_rh2_hand_bringup/share/ruiyan_rh2_hand_bringup/setup/ruiyan_rh2_init.sh
```

Then follow the instructions printed by the script.

Please ensure that the CAN interface specified in the launch arguments matches the one configured by the setup script.

### Joint Position Control
Provides direct joint position command interface:
```bash
ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_joint_position_control.launch.py
```

### Joint Trajectory Control
Provides FollowJointTrajectory action interface for smooth trajectory execution:
```bash
ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_joint_trajectory_control.launch.py
```

### Hand Gripper Position Control
Simplified control for opening/closing the hand:

```bash
ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_gripper_position_control.launch.py
```

## Launch Arguments
All launch files support the following arguments:
- `use_mock_hardware`: Use mock hardware for testing (default: "false")
- `hand_side`: Which hand to control: left or right (default: "left")
- `can_interface`: CAN interface for hand communication (default: "can2")
- `hand_speed`: Speed of hand motors (default: "1000")

### Examples
```bash
# For right hand configuration
ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_joint_trajectory_control.launch.py hand_side:=right can_interface:=can0

# For simulation/testing without physical hand
ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_joint_position_control.launch.py use_mock_hardware:=true
```

## Controllers
Controller configurations are provided in `config/`:
- `controller_manager.yaml`: Controller manager settings and available controllers
- `ruiyan_rh2_hand_joint_position_controller.yaml`: Joint position controller parameters
- `ruiyan_rh2_hand_joint_trajectory_controller.yaml`: Joint trajectory controller parameters

## Hand Descriptions
Complete hand URDF files in `urdf/`:
- `ruiyan_rh2_hand_left.urdf.xacro`: Left hand configuration
- `ruiyan_rh2_hand_right.urdf.xacro`: Right hand configuration

## Joint Information
The hand has 6 controllable joints:
- `thumb_yaw_joint`: Thumb base yaw rotation
- `thumb_pitch_joint`: Thumb base pitch rotation
- `index_proximal_joint`: Index finger base joint
- `middle_proximal_joint`: Middle finger base joint
- `ring_proximal_joint`: Ring finger base joint
- `pinky_proximal_joint`: Pinky finger base joint

## Testing
### Joint Position Test
Run the included test script to validate joint position control:
```bash
# Terminal 1: Launch position controller
ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_joint_position_control.launch.py use_mock_hardware:=true

# Terminal 2: Run test script
python3 /home/ubuntu/ros2_ws/src/robots/ruiyan_rh2_hand/ruiyan_rh2_hand_bringup/test/test_hand_position.py
```

### Joint Trajectory Test
Run the included test script to validate joint trajectory control:
```bash
# Terminal 1: Launch trajectory controller
ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_joint_trajectory_control.launch.py use_mock_hardware:=true

# Terminal 2: Run test script
python3 /home/ubuntu/ros2_ws/src/robots/ruiyan_rh2_hand/ruiyan_rh2_hand_bringup/test/test_hand_trajectory.py
```

### Manual Commands
Test different control modes manually:

**Joint Position Control:**
```bash
# Open hand (all joints to 0)
ros2 topic pub --once /ruiyan_rh2_hand_joint_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}"

# Close hand (typical grasp position)
ros2 topic pub --once /ruiyan_rh2_hand_joint_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.8, 0.4, 1.4, 1.4, 1.4, 1.4]}"
```

**Joint Trajectory Control:**
```bash
ros2 action send_goal /ruiyan_rh2_hand_joint_trajectory_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{
  trajectory: {
    joint_names: [thumb_proximal_yaw_joint, thumb_proximal_pitch_joint, index_proximal_joint, middle_proximal_joint, ring_proximal_joint, pinky_proximal_joint],
    points: [
      { positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: { sec: 2 } },
      { positions: [0.5, 0.2, 0.7, 0.7, 0.7, 0.7], time_from_start: { sec: 4 } },
      { positions: [1.0, 0.4, 1.4, 1.4, 1.4, 1.4], time_from_start: { sec: 6 } },
      { positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: { sec: 9 } }
    ]
  }
}"
```

## Introspection
After launching, you can inspect the system:
```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
ros2 topic list
ros2 service list
```

## Foxglove Studio
An optional layout is available at `config/foxglove/hand_ros2_control.json`. Import it into Foxglove Studio to visualize:
- Joint states
- Controller feedback
- Hand model
- Control topics

The launch files automatically start the foxglove_bridge for web-based visualization.

## Hardware Setup
For physical hand operation:
1. Connect the hand via appropriate interface
2. Use the correct configuration in launch arguments

## Troubleshooting
- **Joint limits**: Ensure commanded positions are within joint limits
- **Mock hardware**: Use `use_mock_hardware:=true` for testing without physical hand

## License and maintainers
Refer to `package.xml` for license and maintainer information.