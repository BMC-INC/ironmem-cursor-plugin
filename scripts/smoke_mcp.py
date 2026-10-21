#!/usr/bin/env python3
"""Exercise the plugin's real MCP transport using only disposable local memory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import queue
import subprocess
import tempfile
import threading

from check_plugin import ROOT, validate
from install_plugin import executable


class MCP:
    def __init__(self, command, config, cwd):
        names = ('PATH', 'SystemRoot', 'WINDIR', 'COMSPEC', 'PATHEXT', 'TMPDIR', 'TEMP', 'TMP')
        env = {key: os.environ[key] for key in names if key in os.environ}
        self.errors = tempfile.TemporaryFile(mode='w+', encoding='utf-8')
        self.process = subprocess.Popen([command[0], '--config', str(config), *command[1:]],
                                        cwd=cwd, env=env, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=self.errors,
                                        text=True, encoding='utf-8')
        self.lines = queue.Queue()
        def read():
            for line in self.process.stdout:
                self.lines.put(line)
            self.lines.put(None)
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        self.serial = 0

    def request(self, method, params):
        self.serial += 1
        message = {'jsonrpc': '2.0', 'id': self.serial, 'method': method, 'params': params}
        self.process.stdin.write(json.dumps(message) + '\n')
        self.process.stdin.flush()
        while True:
            try:
                line = self.lines.get(timeout=60)
            except queue.Empty as error:
                raise RuntimeError('MCP response timed out: ' + method) from error
            if line is None:
                self.errors.seek(0)
                raise RuntimeError('MCP process exited: ' + self.errors.read()[-2000:])
            response = json.loads(line)
            if response.get('id') == self.serial:
                return response

    def initialized(self):
        self.process.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n')
        self.process.stdin.flush()

    def call(self, name, arguments):
        response = self.request('tools/call', {'name': name, 'arguments': arguments})
        if 'error' in response or response.get('result', {}).get('isError'):
            raise RuntimeError('MCP tool failed: ' + json.dumps(response))
        result = response['result']
        text = '\n'.join(c['text'] for c in result.get('content', []) if c.get('type') == 'text')
        return json.loads(text)

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=10)
        self.reader.join(timeout=5)
        self.process.stdout.close()
        self.errors.close()


def smoke(binary):
    package = validate()
    binary = executable(binary)
    definition = json.loads((ROOT / 'mcp.json').read_text(encoding='utf-8'))['mcpServers']['ironmem']
    command = [definition['command'].replace('${IRONMEM_BINARY}', str(binary)), *definition['args']]
    with tempfile.TemporaryDirectory(prefix='ironmem-plugin-smoke-') as directory:
        root = Path(directory)
        project = root / 'project'; project.mkdir()
        config = root / 'settings.json'
        config.write_text(json.dumps({'db_path': str(root / 'memory.db'),
            'embedding': {'provider': 'none'}, 'compression': {'mode': 'local'},
            'rerank': {'enabled': False}, 'observer': {'enabled': False},
            'auto_dream': {'enabled': False}}), encoding='utf-8')
        client = MCP(command, config, project)
        try:
            response = client.request('initialize', {'protocolVersion': '2025-06-18',
                'capabilities': {}, 'clientInfo': {'name': 'ironmem-cursor-plugin-smoke', 'version': '0.1.0'}})
            if 'result' not in response:
                raise RuntimeError('MCP initialization failed: ' + json.dumps(response))
            client.initialized()
            tools = client.request('tools/list', {})['result']['tools']
            names = {tool['name'] for tool in tools}
            required = {'get_status', 'remember', 'search_memories', 'get_context',
                        'retrieve_original', 'wipe_project', 'memory_diagnose'}
            if not required.issubset(names):
                raise RuntimeError('missing required MCP tools')
            if client.call('get_status', {}).get('memories') != 0:
                raise RuntimeError('disposable store was not empty')
            marker = 'IronMem plugin canary cobalt-harbor-791 uses local project memory.'
            client.call('remember', {'project': str(project), 'text': marker,
                'scope': 'project', 'kind': 'project_config', 'classification': 'public'})
            found = client.call('search_memories', {'project': str(project),
                'query': 'cobalt-harbor-791', 'semantic': False, 'limit': 3})
            if marker not in json.dumps(found):
                raise RuntimeError('saved canary was not retrieved')
            context = project / 'IRONMEM.md'
            context.write_text(marker, encoding='utf-8')
            malformed = ['false', 'true', None, 0, [], {}]
            for value in malformed:
                refused = client.request('tools/call', {'name': 'wipe_project',
                    'arguments': {'project': str(project), 'confirm': value}})
                if refused.get('error', {}).get('code') != -32602:
                    raise RuntimeError('malformed wipe confirmation was not refused: ' + repr(value))
                if not context.exists() or client.call('get_status', {})['memories'] != 1:
                    raise RuntimeError('refused wipe changed memory or generated context')
            client.call('wipe_project', {'project': str(project), 'confirm': False})
            if client.call('get_status', {})['memories'] != 1:
                raise RuntimeError('wipe preview changed the store')
            client.call('wipe_project', {'project': str(project), 'confirm': True})
            if client.call('get_status', {})['memories'] != 0:
                raise RuntimeError('confirmed disposable wipe did not delete the canary')
        finally:
            client.close()
    return {'ok': True, 'platform': platform.platform(), 'package': package,
            'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
            'tool_count': len(names), 'save_and_retrieve': True,
            'malformed_confirmations_rejected': len(malformed), 'wipe_preview_and_delete': True,
            'personal_database_opened': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', required=True)
    args = parser.parse_args()
    print(json.dumps(smoke(args.binary), indent=2))
