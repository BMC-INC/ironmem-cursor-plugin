#!/usr/bin/env python3
"""Copy the plugin into Cursor's local plugin directory, retaining older copies."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

from check_plugin import PAYLOAD, ROOT, validate


def hashes(root):
    result = {}
    for path in sorted(Path(root).rglob('*')):
        if path.is_symlink():
            raise ValueError('refusing to replace a plugin containing symlinks')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def executable(value):
    expanded = str(Path(value).expanduser())
    found = shutil.which(expanded)
    if not found:
        raise ValueError('IronMem executable is missing or not executable: ' + expanded)
    binary = Path(found).resolve()
    probe = subprocess.run([str(binary), '--version'], capture_output=True, text=True,
                           check=True, timeout=15)
    if not probe.stdout.strip().startswith('ironmem '):
        raise ValueError('selected executable did not identify itself as IronMem')
    return binary


def install(binary, destination=None, source=ROOT):
    source = Path(source).resolve()
    validate(source)
    binary = executable(binary)
    target = Path(destination or Path.home() / '.cursor/plugins/local/ironmem').expanduser().absolute()
    if target.is_symlink():
        raise ValueError('plugin destination must not be a symlink')
    if target.exists() and not target.is_dir():
        raise ValueError('plugin destination is not a directory')
    if target.resolve().is_relative_to(source) or source.is_relative_to(target.resolve()):
        raise ValueError('plugin source and destination must be separate directories')
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.ironmem-stage-', dir=target.parent))
    backup = None
    try:
        for name in PAYLOAD:
            origin, output = source / name, stage / name
            if origin.is_dir():
                shutil.copytree(origin, output)
            else:
                shutil.copy2(origin, output)
        path = stage / '.cursor-plugin/plugin.json'
        manifest = json.loads(path.read_text(encoding='utf-8'))
        # Cursor's local-plugin loader does not substitute variable defaults.
        # Resolve the command in this local copy; Marketplace users configure
        # the declared variable through Cursor's plugin configuration instead.
        manifest.pop('variables', None)
        path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        mcp_path = stage / 'mcp.json'
        mcp = json.loads(mcp_path.read_text(encoding='utf-8'))
        mcp['mcpServers']['ironmem']['command'] = str(binary)
        mcp_path.write_text(json.dumps(mcp, indent=2) + '\n', encoding='utf-8')
        validate(stage)
        desired = hashes(stage)
        if target.exists():
            previous = hashes(target)
            if desired == previous:
                return {'installed': str(target), 'binary': str(binary), 'changed': False, 'backup': None}
            backups = target.parent.parent / 'backups'
            backups.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            backup = backups / ('ironmem-' + stamp + '-' + uuid.uuid4().hex[:8])
            os.replace(target, backup)
            try:
                if hashes(backup) != previous:
                    raise ValueError('previous plugin backup did not verify')
                os.replace(stage, target)
            except Exception:
                if not target.exists():
                    os.replace(backup, target)
                raise
        else:
            os.replace(stage, target)
        if hashes(target) != desired:
            raise ValueError('installed plugin files did not verify')
        return {'installed': str(target), 'binary': str(binary), 'changed': True,
                'backup': str(backup) if backup else None}
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', required=True, help='Path to an installed trusted IronMem executable')
    parser.add_argument('--destination', type=Path, help='Default: ~/.cursor/plugins/local/ironmem')
    args = parser.parse_args()
    result = install(args.binary, args.destination)
    result['next_step'] = 'Reload Cursor, inspect IronMem in Customize, and call get_status.'
    print(json.dumps(result, indent=2))
