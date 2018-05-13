import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

from pag import utils


class GitTestCase(unittest.TestCase):
    """
    A base class for tests that need a git repo. It creates a temporary repo
    with a single commit for each test and changes to that directory.
    """

    def cmd(self, cmd, cwd=None, *args, **kwargs):
        print('$ %s' % ' '.join(shlex.quote(x) for x in cmd))
        cp = subprocess.run(cmd, *args,
                            cwd=cwd or self.repo,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            **kwargs)
        print(cp.stdout)

    def setUp(self):
        self.orig_path = os.getcwd()
        # Create git repository with some basic content
        self.repo = tempfile.mkdtemp(prefix='test_current_branch_')
        self.cmd(['git', 'init'])
        with open(os.path.join(self.repo, 'file'), 'w') as f:
            f.write('')
        self.cmd(['git', 'add', '.'])
        self.cmd(['git', 'commit', '-m', 'Initial commit'])
        # and chdir into it.
        os.chdir(self.repo)

        # Prepare a directory for creating a clone
        self.clone = tempfile.mkdtemp(prefix='cloned_repo_')

    def tearDown(self):
        shutil.rmtree(self.repo)
        shutil.rmtree(self.clone)
        # Change back to original working directory
        os.chdir(self.orig_path)

    def _clone_to(self, remote, branch):
        if branch != 'master':
            self.cmd(['git', 'checkout', '-b', branch])
        self.cmd(['git', 'clone', self.repo, self.clone, '-o', remote])
        os.chdir(self.clone)


class TestGetDefaultBranch(GitTestCase):
    """
    This test treats the inherited repo as upstream and clones it into a
    separate directory, in which it runs the actual function. It can check out
    a different branch in the "upstream" repo and thus effectively change the
    default branch.
    """

    def test_origin_master(self):
        self._clone_to('origin', 'master')

        self.assertEqual(utils.get_default_upstream_branch(), 'master')

    def test_origin_develop(self):
        self._clone_to('origin', 'develop')

        self.assertEqual(utils.get_default_upstream_branch(), 'develop')

    def test_upstream_master(self):
        self._clone_to('upstream', 'master')

        self.assertEqual(utils.get_default_upstream_branch(), 'master')

    def test_upstream_develop(self):
        self._clone_to('upstream', 'develop')

        self.assertEqual(utils.get_default_upstream_branch(), 'develop')

    def test_no_remote(self):
        self.assertEqual(utils.get_default_upstream_branch(), None)


class TestGetCurrentBranch(GitTestCase):

    def test_single_branch(self):
        self.cmd(['git', 'checkout', '-b', 'test'])
        self.cmd(['git', 'commit', '--allow-empty', '-m', 'Dummy commit'])

        self.assertEqual(utils.get_current_local_branch(), 'test')

    def test_multiple_branches(self):
        # There are two branches pointing at the current commit.
        self.cmd(['git', 'checkout', '-b', 'test'])
        self.cmd(['git', 'commit', '--allow-empty', '-m', 'Dummy commit'])
        self.cmd(['git', 'checkout', '-b', 'another'])

        self.assertEqual(utils.get_current_local_branch(), 'another')

    def test_detached_head(self):
        self.cmd(['git', 'checkout', '-b', 'test'])
        self.cmd(['git', 'commit', '--allow-empty', '-m', 'Dummy commit'])
        self.cmd(['git', 'checkout', 'HEAD^'])

        with self.assertRaises(RuntimeError):
            utils.get_current_local_branch()


class TestGetTrackingBranch(GitTestCase):

    def setUp(self):
        super(TestGetTrackingBranch, self).setUp()
        self._clone_to('origin', 'master')

    def get_test_not_tracking(self, mock_run):
        self.cmd(['git', 'checkout', '-b', 'foo'], cwd=self.clone)
        self.assertEqual(utils.get_tracking_branch(), None)

    def test_with_tracking_branch(self):
        self.cmd(['git', 'checkout', '-b', 'foo'], cwd=self.clone)
        self.cmd(['git', 'push', '-u', 'origin', 'foo:bar'], cwd=self.clone)
        self.assertEqual(utils.get_tracking_branch(), ('origin', 'bar'))

    def test_with_tracking_branch_ahead(self):
        self.cmd(['git', 'checkout', '-b', 'foo'], cwd=self.clone)
        self.cmd(['git', 'push', '-u', 'origin', 'foo:bar'], cwd=self.clone)
        self.cmd(['git', 'commit', '--allow-empty', '-m', 'Dummy commit'],
                 cwd=self.clone)
        self.assertEqual(utils.get_tracking_branch(), ('origin', 'bar'))


class TestGetRemoteUrl(GitTestCase):

    def test_no_remote(self):
        self.assertEqual(utils.get_remote_url('origin'), None)

    def test_with_remote(self):
        self._clone_to('upstream', 'master')
        os.chdir(self.clone)
        self.assertEqual(utils.get_remote_url('upstream'), self.repo)
