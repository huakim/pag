import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

from pag import utils


class TestGetCurrentBranch(unittest.TestCase):

    def cmd(self, cmd, *args, **kwargs):
        print('$ %s' % ' '.join(shlex.quote(x) for x in cmd))
        cp = subprocess.run(cmd, *args,
                            cwd=self.repo,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            **kwargs)
        print(cp.stdout)

    def setUp(self):
        # Create git repository with some basic content
        self.repo = tempfile.mkdtemp(prefix='test_current_branch_')
        self.cmd(['git', 'init'])
        with open(os.path.join(self.repo, 'file'), 'w') as f:
            f.write('')
        self.cmd(['git', 'add', '.'])
        self.cmd(['git', 'commit', '-m', 'Initial commit'])
        # and chdir into it.
        os.chdir(self.repo)

    def tearDown(self):
        shutil.rmtree(self.repo)

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
