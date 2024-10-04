from kubernetes import client, config
from kubernetes.client.rest import ApiException

class PodManager:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    def create_deployment(self, name, image, namespace="default", replicas=1):
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": name}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=name,
                                image=image,
                            )
                        ]
                    )
                )
            )
        )

        try:
            self.apps_v1.create_namespaced_deployment(namespace, deployment)
            print(f"Deployment {name} created successfully.")
        except ApiException as e:
            print(f"Exception when creating deployment: {e}")

    def scale_deployment(self, name, replicas, namespace="default"):
        try:
            self.apps_v1.patch_namespaced_deployment_scale(
                name,
                namespace,
                {"spec": {"replicas": replicas}}
            )
            print(f"Deployment {name} scaled to {replicas} replicas.")
        except ApiException as e:
            print(f"Exception when scaling deployment: {e}")

    def delete_deployment(self, name, namespace="default"):
        try:
            self.apps_v1.delete_namespaced_deployment(name, namespace)
            print(f"Deployment {name} deleted successfully.")
        except ApiException as e:
            print(f"Exception when deleting deployment: {e}")

    def list_pods(self, namespace="default"):
        try:
            pods = self.v1.list_namespaced_pod(namespace)
            return [pod.metadata.name for pod in pods.items]
        except ApiException as e:
            print(f"Exception when listing pods: {e}")
            return []

# Usage example
if __name__ == "__main__":
    pod_manager = PodManager()

    # Create a deployment
    pod_manager.create_deployment("example-deployment", "nginx:latest")

    # Scale the deployment
    pod_manager.scale_deployment("example-deployment", 3)

    # List pods
    print(pod_manager.list_pods())

    # Delete the deployment
    pod_manager.delete_deployment("example-deployment")