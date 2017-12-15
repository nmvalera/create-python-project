"""
    tests.test_scripts_base
    ~~~~~~~~~~~~~~~~~~~~~~~

    Test BaseScript functions

    :copyright: (c) 2017 by Nicolas Maurice, see AUTHORS.rst for more details.
    :license: BSD, see :ref:`license` for more details.
"""

import os

from docutils.io import StringOutput, StringInput, FileInput

from create_python_project.scripts import BaseScript


def test_base_script(repo_path):
    # Test with string input
    script_content = 'test-script-content'
    base_script = BaseScript(source=script_content)
    assert isinstance(base_script.source, StringInput)
    assert isinstance(base_script.destination, StringOutput)
    assert base_script.publish() == script_content

    # Test with string input
    script_content = 'test-script-content\n\n\nextra-line\n'
    base_script = BaseScript(source=script_content)
    assert isinstance(base_script.source, StringInput)
    assert isinstance(base_script.destination, StringOutput)
    assert base_script.publish() == script_content

    # Test with file input
    base_script = BaseScript(source=os.path.join(repo_path, 'setup.py'))
    assert isinstance(base_script.source, FileInput)
    assert isinstance(base_script.destination, StringOutput)

    # Test set_destination and set_source
    base_script.set_destination(None)
    assert isinstance(base_script.destination, StringOutput)
    for dirpath, dirnames, filenames in os.walk(repo_path):
        for filename in filenames:
            base_script.set_source(os.path.join(dirpath, filename))
            assert base_script.source.source_path == os.path.join(dirpath, filename)
            assert base_script.publish() is not None
