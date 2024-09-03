
#Explanation
#List and Build Docs Directories:
#
#This step uses inline shell commands to find all directories containing a docs folder.
#For each directory found, it builds the documentation and copies the result into a temporary artifacts directory.
#Upload All Artifacts:
#
#After all directories are processed, this step uploads the contents of the temporary artifacts directory as a single artifact. GitHub Pages will use this artifact to deploy the site.
#Notes
#Inline Shell Commands:
#
#find applications -type d -name 'docs' -printf '%h\n' lists directories containing docs folders.
#cd "$dir" && make html builds the documentation in each directory.
#cp -r "$dir/build/html" copies the built documentation to a temporary artifacts directory.
#Artifact Handling:
#
#The temporary artifacts directory collects all built documentation.
#The actions/upload-pages-artifact action uploads this directory.
#Deployment:
#
#The actions/deploy-pages action handles the deployment of the collected artifacts to GitHub Pages.
