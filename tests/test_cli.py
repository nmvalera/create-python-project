"""
    tests.test_vli
    ~~~~~~~~~~~~~~

    Test CLI application

    :copyright: Copyright 2017 by Nicolas Maurice, see AUTHORS.rst for more details.
    :license: BSD, see :ref:`license` for more details.
"""

import click

from create_python_project import ProjectManager
from create_python_project.cli import create_python_project, Progress


def test_progress(cli_runner):
    progress = Progress()

    @click.command()
    @click.option('-c', 'op_code', type=int)
    @click.argument('line')
    def test(op_code, line):
        if op_code is None:
            progress.line_dropped(line)
        else:
            progress._cur_line = line
            progress.update(op_code)

    result = cli_runner.invoke(test, ['Line'])
    assert not result.exception
    assert result.output == 'Line\n'

    result = cli_runner.invoke(test, ['-c', 4, 'Current Line'])
    assert not result.exception
    assert result.output == ''

    result = cli_runner.invoke(test, ['-c', 34, 'Current Line'])
    assert not result.exception
    assert result.output == 'Current Line\n'


def test_main_command(cli_runner, manager):
    result = cli_runner.invoke(create_python_project, ['-b', 'git@github.com:nmvalera/boilerplate-python.git',
                                                       '-u', 'https://github.com/nmvalera/new-project-name.git',
                                                       '-a', 'New Author',
                                                       '-e', 'new@author.com',
                                                       'new-project-name'])

    assert result.exit_code == 0

    # Test clone from has been correctly called
    call = ProjectManager.clone_from.call_args_list[0]
    assert call[1]['url'] == 'git@github.com:nmvalera/boilerplate-python.git'
    assert call[1]['to_path'] == 'new-project-name'

    # Test remotes have been correctly updated
    assert list(manager.remotes['boilerplate'].urls) == ['git@github.com:nmvalera/boilerplate-python.git']
    assert list(manager.remotes['origin'].urls) == ['https://github.com/nmvalera/new-project-name.git']

    # Test project has been correctly renamed
    assert manager.get_info(is_filtered='README.rst')[0].title.text == 'New-Project-Name'
    assert manager.get_info(is_filtered='new_project_name/__init__.py')[0].docstring.title.text == 'new_project_name'

    # Test author has been correctly renamed
    assert manager.setup_info.author.value == 'New Author'
    assert manager.setup_info.author_email.value == 'new@author.com'
