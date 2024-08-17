# Helm Charts for Your Project

This directory contains Helm charts and values files used for deploying applications.

## Directory Structure

- `charts/`:
  - Contains Helm charts. Each chart directory includes a `Chart.yaml` and `templates/` directory with Kubernetes manifests.

- `charts/artifactory/`:
  - Contains the Helm chart for JFrog Artifactory. This includes deployment, service, and PVC templates.

- `charts/artifactory-values.yaml`:
  - Custom values file for overriding the default values in `charts/artifactory/values.yaml`.

## Usage

To install or upgrade the Artifactory chart using custom values, use the following command:

```sh
helm upgrade --install artifactory ./resources/charts/artifactory --values ./resources/charts/artifactory-values.yaml
```

## Customization
Edit values.yaml or artifactory-values.yaml to customize the deployment according to your needs.

This setup provides a clear organization for managing your Helm charts and their configurations, making deployment and management of your JFrog Artifactory instance efficient.
