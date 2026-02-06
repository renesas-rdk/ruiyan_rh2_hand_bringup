#!/usr/bin/env python3
# ********************************************************************************************************************
# Copyright [2025] Renesas Electronics Corporation and/or its licensors. All Rights Reserved.
#
# The contents of this file (the "contents") are proprietary and confidential to Renesas Electronics Corporation
# and/or its licensors ("Renesas") and subject to statutory and contractual protections.
#
# Unless otherwise expressly agreed in writing between Renesas and you: 1) you may not use, copy, modify, distribute,
# display, or perform the contents; 2) you may not use any name or mark of Renesas for advertising or publicity
# purposes or in connection with your use of the contents; 3) RENESAS MAKES NO WARRANTY OR REPRESENTATIONS ABOUT THE
# SUITABILITY OF THE CONTENTS FOR ANY PURPOSE; THE CONTENTS ARE PROVIDED "AS IS" WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTY, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NON-INFRINGEMENT; AND 4) RENESAS SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, OR CONSEQUENTIAL DAMAGES,
# INCLUDING DAMAGES RESULTING FROM LOSS OF USE, DATA, OR PROJECTS, WHETHER IN AN ACTION OF CONTRACT OR TORT, ARISING
# OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE CONTENTS. Third-party contents included in this file may
# be subject to different terms.
# ********************************************************************************************************************

"""
Launch file for Ruiyan RH2 Hand with Joint Group Position Controller and Gripper Action Interface

Usage:
  # Mock hardware (no physical hand needed):
  ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_gripper_position_control.launch.py use_mock_hardware:=true

  # Real hardware:
  # Running the setup script to configure CAN interface before launching:
  cd ~/ros2_ws
  ./install/ruiyan_rh2_hand_bringup/share/ruiyan_rh2_hand_bringup/setup/ruiyan_rh2_init.sh
  ros2 launch ruiyan_rh2_hand_bringup ruiyan_rh2_hand_gripper_position_control.launch.py can_interface:=<can_interface> hand_speed:=<hand_speed>

Test commands:
  # Direct joint control:
  ros2 topic pub --once /ruiyan_rh2_hand_joint_position_controller/commands \
    std_msgs/msg/Float64MultiArray "{data: [1.0, 0.5, 1.0, 1.0, 1.0, 1.0]}"

  # Gripper command (topic):
  ros2 topic pub --once /gripper_command \
    control_msgs/msg/GripperCommand "{position: 0.03, max_effort: 10.0}"

  # Gripper command (action with feedback):
  ros2 action send_goal --feedback /gripper_cmd \
    control_msgs/action/ParallelGripperCommand \
    "{command: {position: [0.03], effort: [10.0]}}"
"""

import os
from typing import List

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    """Setup function to evaluate launch configurations at runtime."""
    use_mock_hardware_value = LaunchConfiguration('use_mock_hardware').perform(context)
    hand_side_value = LaunchConfiguration('hand_side').perform(context)
    hand_speed_value = LaunchConfiguration('hand_speed').perform(context)
    can_interface_value = LaunchConfiguration('can_interface').perform(context)
    gripper_mapping_value = LaunchConfiguration('gripper_mapping').perform(context)

    # Get package directories
    pkg_share = get_package_share_directory('ruiyan_rh2_hand_bringup')

    # Use hand-specific XACRO
    if hand_side_value == 'left':
        robot_description_xacro = os.path.join(
            pkg_share, 'urdf', 'ruiyan_rh2_hand_left.urdf.xacro'
        )
    else:
        robot_description_xacro = os.path.join(
            pkg_share, 'urdf', 'ruiyan_rh2_hand_right.urdf.xacro'
        )

    # Process XACRO file
    robot_description_raw = xacro.process_file(
        robot_description_xacro,
        mappings={
            'can_interface': can_interface_value,
            'hand_speed': hand_speed_value,
            'use_mock_hardware': use_mock_hardware_value,
        }
    ).toxml()

    robot_description = {'robot_description': robot_description_raw}

    # Controller management configurations
    controller_config = os.path.join(
        pkg_share, 'config', 'controller_manager.yaml'
    )

    position_controller_config = os.path.join(
        pkg_share, 'config', 'ruiyan_rh2_hand_joint_position_controller.yaml'
    )

    # Foxglove bridge launch file
    foxglove_bridge_launch = os.path.join(
        get_package_share_directory('foxglove_bridge'),
        'launch',
        'foxglove_bridge_launch.xml'
    )

    # Controller manager
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        name='controller_manager',
        output='screen',
        parameters=[
            robot_description,
            controller_config,
            position_controller_config
        ],
        remappings=[
            ('/controller_manager/robot_description', '/robot_description'),
        ],
    )

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    # Joint state broadcaster spawner
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        name='joint_state_broadcaster_spawner',
        output='screen',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    # Hand position controller spawner (starts AFTER joint_state_broadcaster)
    hand_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        name='hand_position_controller_spawner',
        output='screen',
        arguments=[
            'ruiyan_rh2_hand_joint_position_controller',
            '--controller-manager', '/controller_manager',
        ],
    )

    # Hand gripper action adapter
    hand_gripper_action_adapter = Node(
        package='inspire_rh56_hand_utils',
        executable='hand_gripper_action_adapter',
        name='hand_gripper_action_adapter',
        output='screen',
        parameters=[
            {
                'action_server_name': 'gripper_cmd',
                'gripper_command_topic': 'gripper_command',
                'position_controller_topic': '/ruiyan_rh2_hand_joint_position_controller/commands',
                'mapping_config_file': gripper_mapping_value,
                'execution_duration': 1.0,
            }
        ],
    )

    # Foxglove bridge for web-based visualization
    foxglove_bridge_node = IncludeLaunchDescription(
        FrontendLaunchDescriptionSource(foxglove_bridge_launch)
    )

    return [
        controller_manager_node,
        robot_state_publisher_node,
        joint_state_broadcaster_spawner,
        # Start position controller AFTER joint_state_broadcaster finishes
        RegisterEventHandler(
            OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[hand_position_controller_spawner],
            )
        ),
        hand_gripper_action_adapter,
        foxglove_bridge_node,
    ]


def generate_launch_description() -> LaunchDescription:
    """Generate launch description for hand-only testing."""
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_mock_hardware',
            default_value='false',
            description='Use mock hardware for testing (true/false)'
        ),
        DeclareLaunchArgument(
            'hand_side',
            default_value='left',
            description='Which hand to control: left or right'
        ),
        DeclareLaunchArgument(
            'can_interface',
            default_value='can2',
            description='CAN interface for hand hardware communication'
        ),
        DeclareLaunchArgument(
            'hand_speed',
            default_value='1500',
            description='Hand motor speed'
        ),
        DeclareLaunchArgument(
            'gripper_mapping',
            default_value='ruiyan_gripper_joint_mapping_3finger.yaml',
            description='Gripper mapping configuration file'
        ),
        OpaqueFunction(function=launch_setup),
    ])