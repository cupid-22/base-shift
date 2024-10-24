#!/bin/bash
provided_python_version="$1"

# Function to extract Python version from pyproject.toml
get_python_version() {
  toml_file="$1"
  python_version=$(grep 'python' "$toml_file" | cut -d '"' -f2 | cut -d '^' -f2)
  echo "$python_version"
}

# Default Python version if none is found
root_python_version="3.12"
python_versions=()

# Check for Python version in root pyproject.toml
if [[ -f "pyproject.toml" ]]; then
  root_python_version=$(get_python_version "pyproject.toml") || root_python_version="3.10"
  python_versions+=("$root_python_version")
fi

# Check for Python version in each application
for dir in applications/*/; do
  if [[ -f "${dir}pyproject.toml" ]]; then
    app_python_version=$(get_python_version "${dir}pyproject.toml")
    python_versions+=("$app_python_version")
  fi
done

# Deduplicate the list of Python versions
python_versions=($(echo "${python_versions[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

# Combine with input versions, deduplicate again
IFS=',' read -r -a input_versions <<< "$provided_python_version"
all_versions=("${python_versions[@]}" "${input_versions[@]}")

# Deduplicate final versions
final_versions=($(echo "${all_versions[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

echo "Python versions to install: ${final_versions[@]}"
echo "python-versions=${final_versions[*]}" >> $GITHUB_OUTPUT