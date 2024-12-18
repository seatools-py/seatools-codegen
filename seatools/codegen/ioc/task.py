import os
from .common import mkdir, create_file, extract_names, unwrapper_dir_name, str_format
from .cmd import generate_cmd


def generate_task(project_dir: str, package_dir: str, override: bool = False,
                  task_class: str = None,
                  task_name: str = None,
                  is_async: bool = False,
                  cmd: bool = False,
                  docker: bool = False,
                  docker_compose: bool = False,
                  **kwargs):
    """生成任务模板代码."""
    package_name = unwrapper_dir_name(package_dir)
    task_dir = package_dir + os.sep + 'tasks'
    task_init_py = task_dir + os.sep + '__init__.py'
    mkdir(task_dir)
    # 该文件不覆盖, 防止影响其他逻辑
    create_file(task_init_py)

    names = extract_names(task_class)
    task_module_name = '_'.join(names)
    task_py = task_dir + os.sep + task_module_name + '.py'
    if names[-1] != 'task':
        names.append('task')
    custom_task_class = ''.join([(name[0].upper() + name[1:]) if len(name) > 1 else name.upper() for name in names])
    create_file(task_py, '''from typing import Any
from seatools.task import {base_task_class}


class {custom_task_class}({base_task_class}):
    """{task_name}"""

    {async_def_prefix}def _run(self, *args, **kwargs) -> Any:
        # todo: 任务具体逻辑
        pass

    def _task_name(self) -> str:
        return "{task_name}"
'''.format(base_task_class='AsyncTask' if is_async else 'Task', custom_task_class=custom_task_class,
           async_def_prefix='async ' if is_async else '', task_name=task_name), override=override)
    # 需要cmd则创建cmd
    if cmd:
        generate_cmd(project_dir=project_dir,
                     package_dir=package_dir,
                     override=override,
                     command=task_module_name,
                     extra_import=str_format(
                         'from ${package_name}.tasks.${task_module_name} import ${custom_task_class}\n',
                         package_name=package_name,
                         task_module_name=task_module_name,
                         custom_task_class=custom_task_class),
                     extra_run=str_format('${custom_task_class}().run()\n', custom_task_class=custom_task_class),
                     docker=docker,
                     docker_compose=docker_compose,
                     **kwargs)
