cmake_minimum_required(VERSION 3.8)
project(ruiyan_rh2_hand_bringup)

# Find dependencies
find_package(ament_cmake REQUIRED)

# Install config, launch, urdf, and test files
install(
  DIRECTORY
    config
    launch
    urdf
    setup
    test
  DESTINATION share/${PROJECT_NAME}
)

# Install setup files
install(PROGRAMS
  setup/ruiyan_rh2_init.sh
  DESTINATION share/${PROJECT_NAME}/setup
)

# Testing
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()