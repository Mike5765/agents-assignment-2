"""
Option B: Tasks Manager Tools

Implement at least 3 tools for Google Tasks operations.
"""

from typing import Optional
from tools.auth import get_tasks_service


# TODO: Implement your tasks tools
# Define each tool as a plain Python function with a clear docstring and type
# hints (ADK reads these to build the tool schema and auto-wraps the function),
# then add it to the list below. Each tool should return a dict with 'status'
# and relevant data. Wrapping with FunctionTool(func=my_function) is optional
# and only needed when you want explicit control over the tool.


def list_tasks(tasklist_id: str = "@default", show_completed: bool = False,
                max_results: int = 20) -> dict:
    """List tasks from a Google Tasks list.

    Args:
        tasklist_id: ID of the task list to read from.
        show_completed: Whether to include completed tasks.
        max_results: Maximum number of tasks to return.

    Returns:
        dict with 'status' and 'tasks' (list of task dicts).
    """
    try:
        service = get_tasks_service()
        result = service.tasks().list(
            tasklist=tasklist_id,
            showCompleted=show_completed,
            maxResults=max_results,
        ).execute()
        return {"status": "success", "tasks": result.get("items", [])}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
def create_task(title: str, notes: Optional[str] = None, due: Optional[str] = None,
                 tasklist_id: str = "@default") -> dict:
    """Create a new task on a Google Tasks list.

    Args:
        title: Short title describing the task.
        notes: Optional longer description or details for the task.
        due: Optional due date/time in RFC 3339 format
            (e.g. "2026-07-10T00:00:00.000Z").
        tasklist_id: ID of the task list to add to.

    Returns:
        dict with 'status' and 'task' (the created task).
    """
    try:
        service = get_tasks_service()
        body = {"title": title}
        if notes is not None:
            body["notes"] = notes
        if due is not None:
            body["due"] = due

        created = service.tasks().insert(tasklist=tasklist_id, body=body).execute()
        return {"status": "success", "task": created}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
def complete_task(task_id: str, tasklist_id: str = "@default") -> dict:
    """Mark a task as completed.

    Args:
        task_id: The ID of the task to mark complete.
        tasklist_id: ID of the task list the task belongs to.

    Returns:
        dict with 'status' and 'task' (the updated task).
    """
    try:
        service = get_tasks_service()
        updated = service.tasks().patch(
            tasklist=tasklist_id,
            task=task_id,
            body={"status": "completed"},
        ).execute()
        return {"status": "success", "task": updated}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
def update_task(task_id: str, title: Optional[str] = None, notes: Optional[str] = None,
                 due: Optional[str] = None, tasklist_id: str = "@default") -> dict:
    """Update the title, notes, or due date of an existing task.

    Args:
        task_id: The ID of the task to update.
        title: New title for the task, if changing it.
        notes: New notes/description, if changing it.
        due: New due date/time in RFC 3339 format, if changing it.
        tasklist_id: ID of the task list the task belongs to.

    Returns:
        dict with 'status' and 'task' (the updated task), or an error
        if no fields were provided to update.
    """
    try:
        service = get_tasks_service()
        body = {}
        if title is not None:
            body["title"] = title
        if notes is not None:
            body["notes"] = notes
        if due is not None:
            body["due"] = due

        if not body:
            return {"status": "error", "message": "No fields provided to update."}

        updated = service.tasks().patch(
            tasklist=tasklist_id, task=task_id, body=body
        ).execute()
        return {"status": "success", "task": updated}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
def delete_task(task_id: str, tasklist_id: str = "@default") -> dict:
    """Permanently delete a task from a Google Tasks list.

    Args:
        task_id: The ID of the task to delete.
        tasklist_id: ID of the task list the task belongs to.

    Returns:
        dict with 'status' and a confirmation or error 'message'.
    """
    try:
        service = get_tasks_service()
        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        return {"status": "success", "message": f"Task {task_id} deleted."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


tasks_tools = [
    list_tasks,
    create_task,
    complete_task,
    update_task,
    delete_task,
]