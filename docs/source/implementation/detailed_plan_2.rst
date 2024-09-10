# Base Shift Detailed Implementation Plan

.. contents:: Table of Contents
   :depth: 3
   :local:

1. Core Components
==================

1.1 Workflow Manager
--------------------

1.1.1 Overview
~~~~~~~~~~~~~~
The Workflow Manager is the central orchestrator of the Base Shift system. It manages the lifecycle of workflows, coordinates job execution, and maintains the overall state of the system.

1.1.2 Key Features
~~~~~~~~~~~~~~~~~~
- Workflow initialization and termination
- Job scheduling and execution
- State management using Redis
- Error handling and retries

1.1.3 Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
a) Redis Integration
^^^^^^^^^^^^^^^^^^^^
Use Redis as a fast, in-memory data store for workflow states.

Example Redis schema:
```
workflow:{workflowId}:state = "RUNNING"
workflow:{workflowId}:currentJob = "payment_processing"
workflow:{workflowId}:jobs = ["order_validation", "payment_processing", "inventory_update"]
```

b) Job Scheduler
^^^^^^^^^^^^^^^^
Implement a priority queue for job scheduling.

Example job priority logic:
```python
def calculate_job_priority(job):
    base_priority = job.get_base_priority()
    wait_time = time.now() - job.create_time
    return base_priority + (wait_time * 0.1)
```

c) State Machine
^^^^^^^^^^^^^^^^
Implement a state machine to manage workflow states.

Example state transitions:
```
INITIALIZED -> RUNNING -> COMPLETED
         \-> FAILED <-/
```

1.1.4 Interface
~~~~~~~~~~~~~~~
The Workflow Manager exposes a RESTful API for external interactions.

Example endpoints:
- POST /workflows: Create a new workflow
- GET /workflows/{workflowId}: Get workflow status
- PUT /workflows/{workflowId}/jobs/{jobId}: Update job status

1.2 Job Template Store
----------------------

1.2.1 Overview
~~~~~~~~~~~~~~
The Job Template Store is a repository for predefined job templates that can be used to construct workflows.

1.2.2 Key Features
~~~~~~~~~~~~~~~~~~
- CRUD operations for job templates
- Version control for templates
- Template validation

1.2.3 Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
a) Database Schema
^^^^^^^^^^^^^^^^^^
Use a document database like MongoDB for flexible schema evolution.

Example document structure:
```json
{
  "templateId": "payment_gateway_template",
  "version": "1.2.0",
  "steps": [
    {
      "name": "validate_payment_details",
      "type": "validation",
      "config": {
        "rules": ["check_card_number", "check_expiry_date", "check_cvv"]
      }
    },
    {
      "name": "process_payment",
      "type": "external_api_call",
      "config": {
        "api_endpoint": "https://payment.gateway.com/process",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json",
          "Authorization": "Bearer ${API_KEY}"
        }
      }
    }
  ],
  "inputSchema": {
    "type": "object",
    "properties": {
      "amount": {"type": "number"},
      "currency": {"type": "string"},
      "cardDetails": {"type": "object"}
    },
    "required": ["amount", "currency", "cardDetails"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "transactionId": {"type": "string"},
      "status": {"type": "string"}
    },
    "required": ["transactionId", "status"]
  }
}
```

b) Version Control
^^^^^^^^^^^^^^^^^^
Implement semantic versioning for templates.

Example version update logic:
```python
def update_template_version(template, update_type):
    current_version = semver.parse(template['version'])
    if update_type == 'major':
        new_version = semver.bump_major(current_version)
    elif update_type == 'minor':
        new_version = semver.bump_minor(current_version)
    else:
        new_version = semver.bump_patch(current_version)
    template['version'] = str(new_version)
    return template
```

1.2.4 Interface
~~~~~~~~~~~~~~~
Expose a GraphQL API for flexible querying of job templates.

Example GraphQL schema:
```graphql
type JobTemplate {
  id: ID!
  name: String!
  version: String!
  steps: [JobStep!]!
  inputSchema: JSONObject!
  outputSchema: JSONObject!
}

type JobStep {
  name: String!
  type: String!
  config: JSONObject!
}

type Query {
  jobTemplate(id: ID!, version: String): JobTemplate
  jobTemplates(filter: JobTemplateFilter): [JobTemplate!]!
}

input JobTemplateFilter {
  name: String
  version: String
  type: String
}
```

1.3 Pod Management
------------------

1.3.1 Overview
~~~~~~~~~~~~~~
The Pod Management system is responsible for deploying, scaling, and managing the lifecycle of pods that execute jobs.

1.3.2 Key Features
~~~~~~~~~~~~~~~~~~
- On-demand pod deployment
- Auto-scaling based on workload
- Resource optimization
- Pod health monitoring

1.3.3 Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
a) Kubernetes Integration
^^^^^^^^^^^^^^^^^^^^^^^^^
Use the Kubernetes API to manage pods.

Example pod specification:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: job-executor
  labels:
    app: base-shift
    component: job-executor
spec:
  containers:
  - name: job-executor
    image: base-shift/job-executor:v1.0.0
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    env:
    - name: JOB_QUEUE_URL
      value: "redis://job-queue:6379"
    - name: LOG_LEVEL
      value: "INFO"
```

b) Auto-scaling Logic
^^^^^^^^^^^^^^^^^^^^^
Implement Horizontal Pod Autoscaler (HPA) for automatic scaling.

Example HPA configuration:
```yaml
apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: job-executor-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: job-executor
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      targetAverageUtilization: 50
```

c) Resource Optimization
^^^^^^^^^^^^^^^^^^^^^^^^
Implement pod preemption and priority to optimize resource usage.

Example pod priority class:
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "This priority class should be used for critical job pods only."
```

1.3.4 Interface
~~~~~~~~~~~~~~~
Expose a gRPC API for real-time pod management.

Example gRPC service definition:
```protobuf
syntax = "proto3";

package podmanagement;

service PodManager {
  rpc DeployPod(DeployPodRequest) returns (DeployPodResponse) {}
  rpc ScalePods(ScalePodsRequest) returns (ScalePodsResponse) {}
  rpc GetPodStatus(GetPodStatusRequest) returns (GetPodStatusResponse) {}
}

message DeployPodRequest {
  string job_type = 1;
  map<string, string> environment_variables = 2;
}

message DeployPodResponse {
  string pod_id = 1;
  string status = 2;
}

// Additional message definitions...
```

1.4 Event Bus
-------------

1.4.1 Overview
~~~~~~~~~~~~~~
The Event Bus facilitates asynchronous communication between components using a publish-subscribe model.

1.4.2 Key Features
~~~~~~~~~~~~~~~~~~
- Kafka-based messaging system
- Topic management
- Event schema validation
- Dead letter queue for error handling

1.4.3 Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
a) Kafka Setup
^^^^^^^^^^^^^^
Deploy a Kafka cluster with Zookeeper for coordination.

Example Kafka broker configuration:
```properties
broker.id=0
listeners=PLAINTEXT://:9092
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.dirs=/var/lib/kafka/data
num.partitions=1
num.recovery.threads.per.data.dir=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000
zookeeper.connect=zookeeper:2181
zookeeper.connection.timeout.ms=18000
group.initial.rebalance.delay.ms=0
```

b) Topic Management
^^^^^^^^^^^^^^^^^^^
Create a topic management service for dynamic topic creation and configuration.

Example topic creation logic:
```python
from kafka.admin import KafkaAdminClient, NewTopic

def create_topic(topic_name, num_partitions=1, replication_factor=1):
    admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092")
    topic = NewTopic(name=topic_name,
                     num_partitions=num_partitions,
                     replication_factor=replication_factor)
    admin_client.create_topics([topic])
```

c) Event Schema Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^
Use Apache Avro for schema definition and validation.

Example Avro schema for a job completion event:
```json
{
  "type": "record",
  "name": "JobCompletionEvent",
  "fields": [
    {"name": "job_id", "type": "string"},
    {"name": "workflow_id", "type": "string"},
    {"name": "completion_time", "type": "long"},
    {"name": "status", "type": "enum", "symbols": ["SUCCESS", "FAILURE"]},
    {"name": "result", "type": ["null", "string"]}
  ]
}
```

1.4.4 Interface
~~~~~~~~~~~~~~~
Provide a high-level API for publishing and subscribing to events.

Example usage:
```python
from base_shift.event_bus import EventBus

event_bus = EventBus()

# Publishing an event
event_bus.publish("job_completion", {
    "job_id": "1234",
    "workflow_id": "5678",
    "completion_time": 1631234567890,
    "status": "SUCCESS",
    "result": "Payment processed successfully"
})

# Subscribing to events
@event_bus.subscribe("job_completion")
def handle_job_completion(event):
    print(f"Job {event['job_id']} completed with status {event['status']}")
```

2. Workflow Execution Engine
============================

2.1 Workflow Initialization
---------------------------

2.1.1 Overview
~~~~~~~~~~~~~~
The Workflow Initialization component is responsible for setting up new workflows based on predefined templates.

2.1.2 Key Features
~~~~~~~~~~~~~~~~~~
- Template selection and instantiation
- Input validation
- Initial state setup
- Job sequence determination

2.1.3 Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
a) Template Instantiation
^^^^^^^^^^^^^^^^^^^^^^^^^
Create a workflow instance from a template, allowing for customization.

Example instantiation logic:
```python
def instantiate_workflow(template_id, input_data):
    template = job_template_store.get_template(template_id)
    workflow = Workflow(
        id=generate_uuid(),
        template_id=template_id,
        input_data=input_data,
        status="INITIALIZED",
        created_at=datetime.utcnow()
    )
    workflow.jobs = [Job(step) for step in template.steps]
    return workflow
```

b) Input Validation
^^^^^^^^^^^^^^^^^^^
Validate input data against the template's input schema.

Example validation using JSON Schema:
```python
import jsonschema

def validate_input(input_data, schema):
    try:
        jsonschema.validate(instance=input_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"Input validation failed: {e}")
        return False
```

c) State Setup
^^^^^^^^^^^^^^
Initialize the workflow state in Redis.

Example state initialization:
```python
def initialize_workflow_state(workflow):
    redis_client.hmset(f"workflow:{workflow.id}", {
        "status": workflow.status,
        "current_job_index": 0,
        "created_at": workflow.created_at.isoformat()
    })
    redis_client.rpush(f"workflow:{workflow.id}:jobs",
                       *[job.id for job in workflow.jobs])
```

2.1.4 Interface
~~~~~~~~~~~~~~~
Expose a RESTful API endpoint for workflow initialization.

Example API request:
```http
POST /api/v1/workflows
Content-Type: application/json

{
  "template_id": "payment_processing",
  "input_data": {
    "amount": 100.50,
    "currency": "USD",
    "payment_method": "credit_card",
    "card_details": {
      "number": "4111111111111111",
      "expiry": "12/2024",
      "cvv": "123"
    }
  }
}
```

Example API response:
```json
{
  "workflow_id": "wf-123456",
  "status": "INITIALIZED",
  "created_at": "2023-09-08T12:34:56Z",
  "first_job": {
    "id": "job-1",
    "name": "validate_payment_details",
    "status": "PENDING"
  }
}
```

2.2 Job Execution
-----------------

2.2.1 Overview
~~~~~~~~~~~~~~
The Job Execution component is responsible for running individual jobs within a workflow, managing their lifecycle, and handling success or failure scenarios.

2.2.2 Key Features
~~~~~~~~~~~~~~~~~~
- Job dispatch to appropriate pods
- Job status tracking
- Error handling and retries
- Result capturing and storage

2.2.3 Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
a) Job Dispatch
^^^^^^^^^^^^^^^
Implement a job dispatcher that sends jobs to available pods for execution.

Example job dispatch logic:
```python
from kubernetes import client, config

def dispatch_job(job):
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    pod = v1.create_namespaced_pod(
        namespace="default",
        body=client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=f"job-{job.id}",
                labels={"app": "job-executor", "job-id": job.id}
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="job-executor",
                        image="base-shift/job-executor:v1.0.0",
                        env=[
                            client.V1EnvVar(name="JOB_ID", value=job.id),
                            client.V1EnvVar(name="JOB_TYPE", value=job.type)
                        ]
                    )
                ],
                restart_policy="Never
```