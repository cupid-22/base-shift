#!/bin/bash
provided_python_version="$1"

# Function to extract Python version from pyproject.toml
get_python_version() {
  toml_file="$1"
  # Extract the version line for the python dependency
  python_version=$(grep -oP 'python\s*=\s*"\K([^"]+)' "$toml_file" || true)
  echo "$python_version"
}

# Default Python version if none is found
root_python_version="3.12"
python_versions=()

# Check for Python version in root pyproject.toml
if [[ -f "pyproject.toml" ]]; then
  root_python_version=$(get_python_version "pyproject.toml")
  # Fallback to default if not found
  [[ -z "$root_python_version" ]] && root_python_version="3.10"
  python_versions+=("$root_python_version")
fi

# Check for Python version in each application
for dir in applications/*/; do
  if [[ -f "${dir}pyproject.toml" ]]; then
    app_python_version=$(get_python_version "${dir}pyproject.toml")
    # Ensure only valid versions are added
    if [[ -n "$app_python_version" ]]; then
      python_versions+=("$app_python_version")
    fi
  fi
done

# Deduplicate the list of Python versions
mapfile -t unique_python_versions < <(printf "%s\n" "${python_versions[@]}" | sort -u)

# Combine with input versions, deduplicate again
IFS=',' read -r -a input_versions <<< "$provided_python_version"
all_versions=("${unique_python_versions[@]}" "${input_versions[@]}")

# Deduplicate final versions
mapfile -t final_versions < <(printf "%s\n" "${all_versions[@]}" | sort -u)

# Echo the versions correctly
echo "Python versions to install: ${final_versions[*]}"
echo "python-versions=${final_versions[*]}" >> "$GITHUB_OUTPUT"
