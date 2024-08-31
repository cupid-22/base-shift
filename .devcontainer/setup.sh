#!/bin/bash

# Function to generate a random stick figure with colors
generate_stick_figure() {
  # Set colors using ANSI escape codes
  HEAD="\033[1;33mO\033[0m"  # Yellow Head
  ARMS_UP="\033[1;32m \\|/ \033[0m"  # Green Arms up
  ARMS_DOWN="\033[1;32m /|\\ \033[0m"  # Green Arms down
  BODY="\033[1;34m  |  \033[0m"  # Blue Body
  LEGS_TOGETHER="\033[1;35m / \\ \033[0m"  # Magenta Legs together
  LEGS_APART="\033[1;35m / \\ \033[0m"  # Magenta Legs apart

  # Randomly choose the position of the arms and legs
  arms=$((RANDOM % 2))
  legs=$((RANDOM % 2))

  # Stick figure body with random arms and legs positions
  echo -e "  $HEAD  "  # Head
  [ $arms -eq 0 ] && echo -e "$ARMS_UP" || echo -e "$ARMS_DOWN"  # Arms
  echo -e "$BODY"  # Body
  [ $legs -eq 0 ] && echo -e "$LEGS_TOGETHER" || echo -e "$LEGS_APART"  # Legs
}

# Function to print a happy message
print_happy_message() {
  echo -e "\033[1;32mBuild Successful!\033[0m Here's a happy stick figure:"
  echo
}

# Function to provide next steps
print_next_steps() {
  echo -e "\033[1;36mWhat's next?\033[0m"
  echo -e "    - Access the Base Shift frontend at \033[1;34mhttp://localhost:3000\033[0m."
  echo "      This is your main interface for interacting with the application."
  echo -e "    - Monitor your application with Grafana at \033[1;34mhttp://localhost:3001\033[0m."
  echo "      Grafana provides dashboards and visualizations for your application's metrics."
  echo -e "    - Review code quality with SonarQube at \033[1;34mhttp://localhost:9000\033[0m."
  echo "      SonarQube helps ensure your code meets quality standards by analyzing code for bugs, vulnerabilities, and code smells."
  echo
}

# Main script execution
# Wait a bit to ensure all previous outputs are done
sleep 2

# Suppress additional Docker output
clear
print_happy_message
generate_stick_figure
# Delay before the script ends so the stick figure stays visible
sleep 5
echo
print_next_steps
echo
echo
echo