import redis
import json
from uuid import uuid4


class WorkflowManager:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)

    def create_workflow(self, template_id):
        workflow_id = str(uuid4())
        workflow_data = {
            'id': workflow_id,
            'template_id': template_id,
            'status': 'INITIALIZED',
            'current_step': 0,
            'steps': []
        }
        self.redis_client.set(f'workflow:{workflow_id}', json.dumps(workflow_data))
        return workflow_id

    def get_workflow(self, workflow_id):
        workflow_data = self.redis_client.get(f'workflow:{workflow_id}')
        if workflow_data:
            return json.loads(workflow_data)
        return None

    def update_workflow_status(self, workflow_id, status):
        workflow_data = self.get_workflow(workflow_id)
        if workflow_data:
            workflow_data['status'] = status
            self.redis_client.set(f'workflow:{workflow_id}', json.dumps(workflow_data))
            return True
        return False

    def add_workflow_step(self, workflow_id, step_data):
        workflow_data = self.get_workflow(workflow_id)
        if workflow_data:
            workflow_data['steps'].append(step_data)
            workflow_data['current_step'] = len(workflow_data['steps']) - 1
            self.redis_client.set(f'workflow:{workflow_id}', json.dumps(workflow_data))
            return True
        return False

    def get_next_step(self, workflow_id):
        workflow_data = self.get_workflow(workflow_id)
        if workflow_data and workflow_data['current_step'] < len(workflow_data['steps']) - 1:
            workflow_data['current_step'] += 1
            self.redis_client.set(f'workflow:{workflow_id}', json.dumps(workflow_data))
            return workflow_data['steps'][workflow_data['current_step']]
        return None


# Usage example
if __name__ == "__main__":
    wm = WorkflowManager()
    workflow_id = wm.create_workflow("template1")
    print(f"Created workflow: {workflow_id}")

    wm.update_workflow_status(workflow_id, "RUNNING")
    wm.add_workflow_step(workflow_id, {"name": "Step 1", "status": "PENDING"})
    wm.add_workflow_step(workflow_id, {"name": "Step 2", "status": "PENDING"})

    print(wm.get_workflow(workflow_id))
    print(wm.get_next_step(workflow_id))
