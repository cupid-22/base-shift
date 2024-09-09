====================================
Base Shift Detailed Implementation Plan
====================================

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

.. code-block:: text

   workflow:{workflowId}:state = "RUNNING"
   workflow:{workflowId}:currentJob = "payment_processing"
   workflow:{workflowId}:jobs = ["order_validation", "payment_processing", "inventory_update"]

b) Job Scheduler
^^^^^^^^^^^^^^^^
Implement a priority queue for job scheduling.

Example job priority logic:

.. code-block:: python

   def calculate_job_priority(job):
       base_priority = job.get_base_priority()
       wait_time = time.now() - job.create_time
       return base_priority + (wait_time * 0.1)

c) State Machine
^^^^^^^^^^^^^^^^
Implement a state machine to manage workflow states.

Example state transitions:

.. code-block:: text

   INITIALIZED -> RUNNING -> COMPLETED
            \-> FAILED <-/

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

.. code-block:: json

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

b) Version Control
^^^^^^^^^^^^^^^^^^
Implement semantic versioning for templates.

Example version update logic:

.. code-block:: python

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

1.2.4 Interface
~~~~~~~~~~~~~~~
Expose a GraphQL API for flexible querying of job templates.

Example GraphQL schema:

.. code-block:: graphql

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

.. code-block:: yaml

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
