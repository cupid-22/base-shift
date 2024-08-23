#!/usr/bin/env python3

import json
import os
import shutil


def parse_gitignore(file_path):
    """ Parse .gitignore file to get the list of ignored patterns. """
    ignored_patterns = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                ignored_patterns.append(line)
    return ignored_patterns


def should_ignore(file_path, patterns):
    """ Check if a file should be ignored based on .gitignore patterns. """
    for pattern in patterns:
        if pattern in file_path:
            return True
    return False


def main():
    base_dir = '/workspace'
    gitignore_path = os.path.join(base_dir, '.gitignore')
    ignored_patterns = parse_gitignore(
        gitignore_path) if os.path.exists(gitignore_path) else []

    workspace_config = {
        "folders": [],
        "settings": {
            "python.pythonPath": "/usr/local/bin/python",
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "files.autoSave": "onWindowChange"
        }
    }

    # Workspace for docs folders
    docs_workspace = {"path": "docs"}

    # Workspace for root level folders starting with a dot
    dotfolders_workspace = {"path": "dotfolders"}

    # Workspace for ignored files
    gitignore_workspace = {"path": "gitignore"}

    # Create the workspaces
    workspace_config["folders"].append(docs_workspace)
    workspace_config["folders"].append(dotfolders_workspace)
    workspace_config["folders"].append(gitignore_workspace)

    # Add docs/* folders
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path) and folder_name.startswith('docs'):
            workspace_config["folders"].append({
                "path": os.path.join('docs', folder_name),
                "name": folder_name.capitalize()
            })

    # Add root level dotfolders
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path) and folder_name.startswith('.'):
            workspace_config["folders"].append({
                "path": folder_name,
                "name": folder_name[1:].capitalize()
            })

    # Add files and folders ignored by .gitignore
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path) and should_ignore(folder_name, ignored_patterns):
            workspace_config["folders"].append({
                "path": os.path.join('gitignore', folder_name),
                "name": folder_name
            })

    # Save to a .code-workspace file
    workspace_file = os.path.join(base_dir, 'project.code-workspace')
    with open(workspace_file, 'w') as f:
        json.dump(workspace_config, f, indent=4)

    # Copy workspace file to volume
    volume_dir = '/mnt/workspace-config'
    if not os.path.exists(volume_dir):
        os.makedirs(volume_dir)
    shutil.copy(workspace_file, volume_dir)


if __name__ == "__main__":
    main()
