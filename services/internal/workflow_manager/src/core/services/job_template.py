import json
import os


class JobTemplateStore:
    def __init__(self, storage_path='job_templates.json'):
        self.storage_path = storage_path
        self.templates = self._load_templates()

    def _load_templates(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_templates(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.templates, f, indent=2)

    def create_template(self, template_id, template_data):
        if template_id in self.templates:
            raise ValueError(f"Template with id {template_id} already exists")
        self.templates[template_id] = template_data
        self._save_templates()

    def get_template(self, template_id):
        return self.templates.get(template_id)

    def update_template(self, template_id, template_data):
        if template_id not in self.templates:
            raise ValueError(f"Template with id {template_id} does not exist")
        self.templates[template_id] = template_data
        self._save_templates()

    def delete_template(self, template_id):
        if template_id not in self.templates:
            raise ValueError(f"Template with id {template_id} does not exist")
        del self.templates[template_id]
        self._save_templates()

    def list_templates(self):
        return list(self.templates.keys())


# Usage example
if __name__ == "__main__":
    store = JobTemplateStore()

    # Create a new template
    store.create_template("template1", {
        "name": "Simple Workflow",
        "steps": [
            {"name": "Step 1", "type": "python_script", "script": "print('Hello, World!')"},
            {"name": "Step 2", "type": "shell_command", "command": "echo 'Done!'"}
        ]
    })

    # Get and print a template
    print(store.get_template("template1"))

    # Update a template
    store.update_template("template1", {
        "name": "Updated Simple Workflow",
        "steps": [
            {"name": "Step 1", "type": "python_script", "script": "print('Hello, Updated World!')"},
            {"name": "Step 2", "type": "shell_command", "command": "echo 'Done!'"},
            {"name": "Step 3", "type": "python_script", "script": "print('New step!')"}
        ]
    })

    # List all templates
    print(store.list_templates())

    # Delete a template
    store.delete_template("template1")