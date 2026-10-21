#!/usr/bin/env python3
"""Check this single Cursor plugin against its documented package contract."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parent.parent
PAYLOAD = ('.cursor-plugin', 'mcp.json', 'assets', 'skills', 'rules', 'commands',
           'README.md', 'PRIVACY.md', 'TERMS.md', 'SECURITY.md', 'LICENSE', 'NOTICE')


def relative_path(root, value):
    if not isinstance(value, str) or not value:
        raise ValueError('component path must be a nonempty string')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or '\\' in value or ':' in value:
        raise ValueError('component paths must be portable repository-relative paths')
    result = root / value
    if not result.exists() or not result.resolve().is_relative_to(root.resolve()):
        raise ValueError('missing component or component outside plugin: ' + value)
    return result


def frontmatter(path):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    if not lines or lines[0] != '---' or '---' not in lines[1:]:
        raise ValueError('missing frontmatter: ' + str(path))
    end = lines.index('---', 1)
    fields = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(':')
        if not separator or not value.strip():
            raise ValueError('invalid frontmatter: ' + str(path))
        fields[key.strip()] = value.strip()
    if not fields.get('description') or not '\n'.join(lines[end + 1:]).strip():
        raise ValueError('missing description or instructions: ' + str(path))
    return fields


def validate(root=ROOT):
    root = Path(root).resolve()
    manifest = json.loads((root / '.cursor-plugin/plugin.json').read_text(encoding='utf-8'))
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', manifest['name']):
        raise ValueError('invalid plugin name')
    if not re.fullmatch(r'\d+\.\d+\.\d+', manifest['version']):
        raise ValueError('invalid semantic version')
    for key in ('description', 'author', 'repository', 'license'):
        if not manifest.get(key):
            raise ValueError('missing manifest field: ' + key)
    if manifest['license'] != 'Apache-2.0':
        raise ValueError('plugin license must match LICENSE')
    for key in ('repository', 'homepage'):
        if manifest[key] != 'https://github.com/BMC-INC/ironmem-cursor-plugin':
            raise ValueError('unexpected public repository URL')
    logo = relative_path(root, manifest['logo'])
    if not logo.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('logo is not a PNG')
    for key in ('skills', 'rules', 'commands', 'mcpServers'):
        relative_path(root, manifest[key])
    variables = manifest['variables']
    if variables.get('type') != 'object' or not isinstance(variables.get('properties'), dict):
        raise ValueError('variables must be an object JSON Schema')
    config = json.loads((root / manifest['mcpServers']).read_text(encoding='utf-8'))
    referenced = set(re.findall(r'\$\{([A-Z_][A-Z_0-9]*)\}', json.dumps(config)))
    if referenced != set(variables['properties']):
        raise ValueError('MCP variables must match declared plugin variables')
    servers = config.get('mcpServers', {})
    if set(servers) != {'ironmem'}:
        raise ValueError('package must define the local ironmem server')
    server = servers['ironmem']
    if server != {'command': '${IRONMEM_BINARY}', 'args': ['mcp']}:
        raise ValueError('MCP must directly launch IronMem stdio without a shell or listener')
    components = {}
    for kind, pattern in (('skills', '*/SKILL.md'), ('rules', '*.mdc'), ('commands', '*.md')):
        paths = sorted(relative_path(root, manifest[kind]).glob(pattern))
        if not paths:
            raise ValueError('missing ' + kind)
        for path in paths:
            fields = frontmatter(path)
            if kind != 'rules' and not fields.get('name'):
                raise ValueError('missing component name: ' + str(path))
            if kind == 'skills' and fields['name'] != path.parent.name:
                raise ValueError('skill directory and name disagree')
        components[kind] = len(paths)
    for item in PAYLOAD:
        path = relative_path(root, item)
        candidates = [path, *path.rglob('*')] if path.is_dir() else [path]
        for candidate in candidates:
            if candidate.is_symlink():
                raise ValueError('plugin payload must not contain symlinks')
            if candidate.is_file() and candidate.suffix.lower() in ('.exe', '.dll', '.so', '.dylib', '.db'):
                raise ValueError('runtime binary or personal database in plugin payload')
    return {'name': manifest['name'], 'version': manifest['version'], 'components': components,
            'mcp_transport': 'stdio', 'variables': sorted(referenced)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(validate(args.root), indent=2))
