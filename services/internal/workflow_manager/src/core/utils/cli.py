import click
import json
from services.internal.workflow_manager.src.core.services.workflow_manager import WorkflowManager
from services.internal.workflow_manager.src.core.services.job_template import JobTemplateStore


@click.group()
def cli():
    """Base Shift CLI for managing job templates and workflows."""
    pass


@cli.command()
@click.option('--name', prompt='Enter the template name', help='Name of the job template')
@click.option('--steps', prompt='Enter the steps as JSON', help='Steps of the job template in JSON format')
def add_template(name, steps):
    """Add a new job template."""
    store = JobTemplateStore()
    try:
        steps_json = json.loads(steps)
        template_id = f"template_{len(store.list_templates()) + 1}"
        template_data = {
            "name": name,
            "steps": steps_json
        }
        store.create_template(template_id, template_data)
        click.echo(f"Template '{name}' added successfully with ID: {template_id}")
    except json.JSONDecodeError:
        click.echo("Error: Steps must be valid JSON")
    except Exception as e:
        click.echo(f"Error adding template: {str(e)}")


@cli.command()
def list_templates():
    """List all job templates."""
    store = JobTemplateStore()
    templates = store.list_templates()
    if templates:
        click.echo("Available job templates:")
        for template_id in templates:
            template = store.get_template(template_id)
            click.echo(f"- {template_id}: {template['name']}")
    else:
        click.echo("No job templates found.")


@cli.command()
@click.option('--template-id', prompt='Enter the template ID', help='ID of the job template to use')
def run_workflow(template_id):
    """Run a new workflow based on a job template."""
    store = JobTemplateStore()
    wm = WorkflowManager()

    template = store.get_template(template_id)
    if template:
        workflow_id = wm.create_workflow(template_id)
        click.echo(f"New workflow started with ID: {workflow_id}")

        # Add steps from the template to the workflow
        for step in template['steps']:
            wm.add_workflow_step(workflow_id, step)

        wm.update_workflow_status(workflow_id, "RUNNING")
        click.echo("Workflow is now running.")
    else:
        click.echo(f"Error: Template with ID {template_id} not found.")


if __name__ == '__main__':
    cli()
