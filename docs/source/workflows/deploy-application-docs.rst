=======================
Build and Deploy Sphinx Docs
=======================

This document explains the GitHub Actions workflow for building and deploying Sphinx documentation, including steps to work with it, how to run the workflow, and how to debug issues.

Overview
--------

The workflow automates the process of building and deploying Sphinx documentation to GitHub Pages. It does the following:

1. **Checks out the repository**: Retrieves the latest code from the repository.
2. **Sets up Python**: Configures the Python environment needed for Sphinx.
3. **Installs Poetry**: Manages Python dependencies using Poetry.
4. **Installs documentation dependencies**: Uses Poetry to install the necessary packages for building the documentation.
5. **Builds the root Sphinx documentation**: Compiles the Sphinx documentation located in the root `docs` directory.
6. **Finds and builds documentation in subdirectories**: Locates all `docs` directories under `applications`, builds the documentation for each, and copies the results.
7. **Lists artifacts**: Provides a debug output of the built documentation.
8. **Uploads artifacts**: Uploads the built documentation to GitHub as artifacts.
9. **Deploys to GitHub Pages**: Publishes the documentation to GitHub Pages.
10. **Notifies success or failure**: Alerts if the build and deployment were successful or failed.

Details
--------

### 1. Checkout the Repository

This step uses `actions/checkout@v3` to clone the repository so that the workflow can access the files and directories within it.

### 2. Set Up Python

The `actions/setup-python@v4` action sets up the required Python version (3.x) for running the build commands.

### 3. Install Poetry

Poetry is installed to manage Python dependencies. This is done using pip:

    python -m pip install --upgrade pip
    pip install poetry

### 4. Install Documentation Dependencies

Dependencies specific to documentation are installed using Poetry:

    poetry install --only docs --no-root

### 5. Build Root Sphinx Documentation

The root Sphinx documentation is built by running `make html` in the `docs` directory. This ensures that the root documentation is properly compiled.

### 6. List and Build Docs Directories

This step uses a shell script to:

- Find all directories with a `docs` folder.
- Build the Sphinx documentation in each directory.
- Copy the built HTML files to a temporary artifacts directory.

Shell Commands:

    for dir in $(find applications -type d -name 'docs' -printf '%h\n'); do
      app_name=$(basename $dir)
      echo "Processing $app_name in $dir"

      # Change to the directory containing the 'docs' folder
      (cd "$dir/docs" && make html)

      # Check if the Sphinx build was successful by verifying the presence of index.html
      if [ -f "$dir/docs/build/html/index.html" ]; then
        echo "index.html found in $dir"
      else
        echo "Error: index.html not found in $dir"
        exit 1
      fi

      # Create a directory in the artifacts folder named after the application
      mkdir -p $GITHUB_WORKSPACE/artifacts/$app_name

      # Copy the built HTML documentation to the artifacts folder
      cp -r "$dir/docs/build/html/"* $GITHUB_WORKSPACE/artifacts/$app_name/
    done

### 7. List Artifacts

The `ls -R artifacts/` command is used to list the contents of the artifacts directory for debugging purposes.

### 8. Upload All Artifacts

The `actions/upload-pages-artifact@v3` action uploads the contents of the `artifacts` directory so that it can be used for deployment.

### 9. Deploy to GitHub Pages

The `actions/deploy-pages@v4` action publishes the uploaded artifacts to GitHub Pages using the repository's GitHub token.

### 10. Notify Success or Failure

After deployment, a notification is printed to indicate whether the build and deployment were successful or failed.

Running the Workflow
--------------------

The workflow is triggered automatically on `push` and `pull_request` events to the `main` branch, or manually via `workflow_dispatch`.

To run the workflow manually:

1. Go to the Actions tab in your GitHub repository.
2. Select the "Build and Deploy Application Sphinx Docs" workflow.
3. Click on "Run workflow".

Debugging
---------

To debug issues with the workflow:

1. **Check Logs**: Review the logs for each step in the GitHub Actions interface. They provide details about the execution of commands and any errors encountered.

2. **List Artifacts**: Use the debug step that lists the artifacts (`List artifacts (for debugging) 🧐`) to ensure that all expected files are present.

3. **Verify Index File**: Ensure that `index.html` is present in the `docs/build/html` directory after the build step. If it's missing, check for build errors in the Sphinx build process.

4. **Re-run Workflow**: Make changes to the workflow or documentation, and re-run the workflow to test fixes.

Additional Resources
--------------------

- `GitHub Actions Documentation <https://docs.github.com/en/actions>`_
- `Sphinx Documentation <https://www.sphinx-doc.org/en/master/>`_
- `Poetry Documentation <https://python-poetry.org/docs/>`_

By following these instructions, you can understand, run, and troubleshoot the GitHub Actions workflow for building and deploying Sphinx documentation.
