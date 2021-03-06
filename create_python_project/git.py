"""
    create_python_project.git
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements functions to enable automatic manipulations of a project as a git repository

    :copyright: Copyright 2017 by Nicolas Maurice, see AUTHORS.rst for more details.
    :license: BSD, see :ref:`license` for more details.
"""

from functools import partial

from git import Repo

from .utils import is_matching


class RepositoryManager(Repo):
    """Implements functions to automatically manipulate the project has a git repository"""

    COMMIT_MSG_POSTFIX = '(this commit has been generated by Create-Python-Project)'

    def apply_func(self, func, *args, is_filtered=None, tree=None, **kwargs):
        """Apply a function to every blob in a git tree (each blob corresponding to a script track by git)

        You can apply the function only on a subset of the git tree by precising is_filtered argument.

        :param func: A function taking a blob as first argument
        :param args: Optional extra arguments that will be provided to the function
            (can be a function taking blob as argument)
        :param is_filtered: Optional function taking a blob as argument and returning a boolean.
            It can also be a string that will be interpreted as a path folder pattern in .gitignore format
        :param tree: Optional git tree to apply function on
        :param kwargs: Optional extra keyword arguments to provide to the function
            (can be a function taking blob as argument)
        :return:
        """
        tree = tree or self.tree()

        if isinstance(is_filtered, str):
            is_filtered = [is_filtered]

        if isinstance(is_filtered, list):
            is_filtered = partial(is_matching, is_filtered)

        for blob in tree.blobs:
            if not callable(is_filtered) or is_filtered(blob):
                func(blob,
                     *[arg(blob) if callable(arg) else arg for arg in args],
                     **{kw: arg(blob) if callable(arg) else arg for kw, arg in kwargs.items()})

        for sub_tree in tree.trees:
            self.apply_func(func, is_filtered=is_filtered, tree=sub_tree, *args, **kwargs)

    def commit(self, *args, **kwargs):
        """Commit modification

        It is a abstraction over regular repo.git.commit function.
        That first ensure the project has some modifications to commit before committing
        """

        if self.is_dirty():
            self.git.commit(*args, **kwargs)

    def get_tags(self):
        """Return ordered list of tags of the project ordered from most recent to oldest"""

        return sorted(self.tags, key=lambda tag: tag.commit.committed_datetime, reverse=True)

    def get_blobs(self, is_filtered=None):
        """Explore the git repository tree in order to list all scripts that are tracked by git

        :param tree: Repository tree
        :type tree: Tree

        :return: List of scripts paths
        """

        blobs = []
        self.apply_func(lambda blob: blobs.append(blob), is_filtered=is_filtered)

        return blobs

    def get_commits(self, from_rev=None):
        """Retrieve commits from a given revision

        :param from_tag: Optional revision from which to retrieve commits (usually a tag name or a commit hash)
        :type from_tag: str

        Usually you need to retrieve all commits from a given tag or a given commit

            from create_python_project.git import RepositoryManager
            repo = RepositoryManager(path)
            repo.get_commits('v0.1.1')
            repo.get_commits('715dfb6a60eb69aea9b7d32411e445efaa6389b1')
        """
        rev = '...{from_rev}'.format(from_rev=from_rev) if from_rev else None
        return list(self.iter_commits(rev))

    def push(self, push_tags=True):
        """Push project

        :param push_tags: Optional boolean indicating whether or not to push tags
        :type push_tags: bool
        """
        extra_args = ['--follow-tags'] if push_tags else []
        self.git.push(*extra_args)

    def mv(self, old_path, new_path):
        """Rename a folder

        :param old_path: Old folder to be rename
        :type old_path: str
        :param new_path: New folder name
        :type new_path: str
        """

        self.git.mv(old_path, new_path)

        # Commit modification
        message_pattern = 'refactor(all): rename folder {old_path} to {new_path}\n' \
                          '\n' \
                          '{postfix}'
        self.commit(old_path, new_path, '-m', self.make_message(message_pattern, old_path=old_path, new_path=new_path))

    def make_message(self, message_pattern, **kwargs):
        """Compute a message from a message pattern"""
        return message_pattern.format(**kwargs, postfix=self.COMMIT_MSG_POSTFIX)
