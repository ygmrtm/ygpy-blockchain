try:
    import random
    import time
    from todoist_api_python.api import TodoistAPI
    from jproperties import Properties
except ImportError as exc:
    raise exc


def load_properties():
    configs = Properties()
    with open('../blockchain.properties', 'rb') as read_prop:
        configs.load(read_prop)
    return configs


def get_property(key):
    configs = load_properties()
    return configs[key].data


def get_chain(blockchain):
    chain_data = []
    for block in blockchain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


def get_todoist_api():
    return TodoistAPI(get_property('TODOIST_APITOKEN'))


def get_project(project_id):
    project = None
    try:
        api = get_todoist_api()
        project = api.get_project(project_id=project_id)
    except Exception as error:
        print(error)
    return project


def get_tasks(project_id, section_id):
    try:
        api = get_todoist_api()
        tasks = api.get_tasks(project_id=project_id, section_id=section_id)
        return tasks
    except Exception as error:
        print(error)
        raise


def get_pending_tasks():
    _pending_tasks = get_tasks(get_property('TODOIST_PROJECT_ID'), get_property('TODOIST_SECTION_ID'))
    print(f'There are {len(_pending_tasks)} pending transactions (whole universe)')
    _pending_tasks.sort(key=lambda x: x.content and x.priority, reverse=False)
    return _pending_tasks


def add_comment(task_id, content):
    try:
        api = get_todoist_api()
        comment = api.add_comment(
            content=content,
            task_id=task_id
        )
        return comment
    except Exception as error:
        print(error)
        raise


def update_task(task_id, label_ids):
    try:
        api = get_todoist_api()
        label_ids.append(int(get_property('TODOIST_MINED_LABEL_ID')))
        is_success = api.update_task(task_id=task_id, due_string="today", label_ids=label_ids)
        return is_success
    except Exception as error:
        print(error)
        raise


def close_task(task_id):
    try:
        api = get_todoist_api()
        is_success = api.close_task(task_id=task_id)
        return is_success
    except Exception as error:
        print(error)
        raise


if __name__ == "__main__":
    pending_tasks = get_project(2995104339)
