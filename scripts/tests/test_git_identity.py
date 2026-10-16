"""在临时仓库中验证身份钩子，所有提交和配置都限于临时目录。"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
NAME = '4evour'
EMAIL = '167200760+4evour@users.noreply.github.com'


class GitIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='git identity ')
        self.addCleanup(temporary.cleanup)
        self.repository = Path(temporary.name)
        self.environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
        self.environment.update({'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull})
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', '历史作者')
        self.git('config', 'user.email', 'history@example.com')
        self.git('commit', '-q', '--allow-empty', '-m', '已有远端历史')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.git('update-ref', 'refs/remotes/origin/main', self.base)
        shutil.copytree(ROOT / '.githooks', self.repository / '.githooks')
        for key, value in {'user.name': NAME, 'user.email': EMAIL, 'identity.name': NAME,
                           'identity.email': EMAIL, 'core.hooksPath': '.githooks'}.items():
            self.git('config', key, value)
        executable = Path(shutil.which('git')).resolve()
        candidates = [executable.parent.parent / 'bin' / 'sh.exe', executable.parent / 'sh.exe']
        self.shell = shutil.which('sh') or next((str(path) for path in candidates if path.is_file()), None)
        if not self.shell:
            self.fail('未找到 Git 使用的 sh。')

    def git(self, *arguments, check=True, overrides=None):
        return subprocess.run(['git', *arguments], cwd=self.repository, env={**self.environment, **(overrides or {})},
                              text=True, encoding='utf-8', capture_output=True, check=check)

    def commit(self, **overrides):
        return self.git('commit', '-q', '--allow-empty', '-m', '待上传更新', check=False, overrides=overrides)

    def push_hook(self, remote=None, local=None):
        head = local or self.git('rev-parse', 'HEAD').stdout.strip()
        reference = f'refs/heads/main {head} refs/heads/main {remote or self.base}\n'
        return subprocess.run([self.shell, '.githooks/pre-push', 'origin', 'unused'], cwd=self.repository,
                              env=self.environment, input=reference.encode('utf-8'), capture_output=True)

    def test_correct_identity_and_existing_history_are_accepted(self):
        self.assertEqual(self.commit().returncode, 0)
        self.assertEqual(self.push_hook().returncode, 0)

    def test_wrong_local_configuration_is_rejected(self):
        self.git('config', 'user.email', 'company@example.com')
        self.assertNotEqual(self.commit().returncode, 0)

    def test_author_environment_override_is_rejected(self):
        self.assertNotEqual(self.commit(GIT_AUTHOR_NAME='wrong').returncode, 0)

    def test_committer_environment_override_is_rejected(self):
        self.assertNotEqual(self.commit(GIT_COMMITTER_EMAIL='company@example.com').returncode, 0)

    def test_push_rejects_earlier_bad_author_even_when_latest_is_correct(self):
        self.git('-c', 'core.hooksPath=', 'commit', '-q', '--allow-empty', '--author=wrong <wrong@example.com>', '-m', '错误作者')
        self.assertEqual(self.commit().returncode, 0)
        self.assertNotEqual(self.push_hook().returncode, 0)

    def test_push_rejects_wrong_committer(self):
        self.git('-c', 'core.hooksPath=', 'commit', '-q', '--allow-empty', '-m', '错误提交者', overrides={'GIT_COMMITTER_NAME': 'wrong'})
        self.assertNotEqual(self.push_hook().returncode, 0)

    def test_new_branch_checks_only_commits_missing_from_remote(self):
        self.assertEqual(self.commit().returncode, 0)
        self.assertEqual(self.push_hook(remote='0' * 40).returncode, 0)
        self.git('-c', 'core.hooksPath=', 'commit', '-q', '--allow-empty', '--author=wrong <wrong@example.com>', '-m', '错误作者')
        self.assertNotEqual(self.push_hook(remote='0' * 40).returncode, 0)

    def test_unknown_remote_base_is_rejected(self):
        self.assertNotEqual(self.push_hook(remote='f' * 40).returncode, 0)

    def test_deleting_a_reference_does_not_scan_history(self):
        self.assertEqual(self.push_hook(local='0' * 40).returncode, 0)


if __name__ == '__main__':
    unittest.main()
