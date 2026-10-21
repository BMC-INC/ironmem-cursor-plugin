import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from check_plugin import ROOT, validate
from install_plugin import hashes, install


class Installation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='ironmem-plugin-install-test-')
        self.root = Path(self.temporary.name)
        self.target = self.root / 'plugins/local/ironmem'
        self.binary = Path(sys.executable).resolve()
        self.probe = patch('install_plugin.subprocess.run', return_value=subprocess.CompletedProcess(
            [str(self.binary), '--version'], 0, stdout='ironmem 0.4.0\n', stderr=''))
        self.probe.start()

    def tearDown(self):
        self.probe.stop()
        self.temporary.cleanup()

    def test_copy_and_idempotence_preserve_other_plugins(self):
        other = self.target.parent / 'other-plugin'
        other.mkdir(parents=True)
        (other / 'keep.txt').write_text('unrelated', encoding='utf-8')
        first = install(str(self.binary), self.target)
        self.assertTrue(first['changed'])
        data = json.loads((self.target / '.cursor-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertNotIn('variables', data)
        mcp = json.loads((self.target / 'mcp.json').read_text(encoding='utf-8'))
        self.assertEqual(mcp['mcpServers']['ironmem'], {'command': str(self.binary), 'args': ['mcp']})
        self.assertNotIn('${', json.dumps(mcp), 'local MCP commands must be executable without dashboard substitution')
        before = hashes(self.target)
        self.assertFalse(install(str(self.binary), self.target)['changed'])
        self.assertEqual(hashes(self.target), before)
        self.assertEqual((other / 'keep.txt').read_text(encoding='utf-8'), 'unrelated')
        self.assertEqual(validate(self.target)['mcp_transport'], 'stdio')

    def test_upgrade_keeps_previous_copy_and_custom_files(self):
        install(str(self.binary), self.target)
        (self.target / 'custom-note.txt').write_text('keep this older local change', encoding='utf-8')
        before = hashes(self.target)
        result = install(str(self.binary), self.target)
        backup = Path(result['backup'])
        self.assertEqual(hashes(backup), before)
        self.assertFalse(backup.is_relative_to(self.target.parent))
        self.assertFalse((self.target / 'custom-note.txt').exists())

    def test_replacement_failure_restores_previous_copy(self):
        install(str(self.binary), self.target)
        (self.target / 'custom-note.txt').write_text('restore me', encoding='utf-8')
        before = hashes(self.target)
        import os
        rename = os.replace
        def fail_new_copy(source, destination):
            if Path(source).name.startswith('.ironmem-stage-'):
                raise OSError('simulated replacement failure')
            return rename(source, destination)
        with patch('install_plugin.os.replace', side_effect=fail_new_copy):
            with self.assertRaisesRegex(OSError, 'simulated'):
                install(str(self.binary), self.target)
        self.assertEqual(hashes(self.target), before)

    def test_rejects_non_ironmem_and_unsafe_destination(self):
        with patch('install_plugin.subprocess.run', return_value=subprocess.CompletedProcess(
                [], 0, stdout='unrelated executable\n', stderr='')):
            with self.assertRaisesRegex(ValueError, 'identify itself'):
                install(str(self.binary), self.target)
        self.assertFalse(self.target.exists())
        self.target.parent.mkdir(parents=True)
        self.target.write_text('not a plugin directory', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'not a directory'):
            install(str(self.binary), self.target)
        self.assertEqual(self.target.read_text(encoding='utf-8'), 'not a plugin directory')
        with self.assertRaisesRegex(ValueError, 'separate directories'):
            install(str(self.binary), ROOT / 'nested-target')

    def test_binary_with_shell_metacharacters_stays_literal(self):
        # Exercise path handling and argv construction; never invoke a shell.
        fake = self.root / ("ironmem 'quotes' $HOME `literal`" + ('.exe' if sys.platform == 'win32' else ''))
        shutil.copy2(self.binary, fake)
        fake.chmod(0o755)
        result = install(str(fake), self.target)
        self.assertEqual(result['binary'], str(fake.resolve()))


if __name__ == '__main__':
    unittest.main()
