#!/usr/bin/env python3
"""Package source files for a ZCode local marketplace. Not installed in plugin."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'

def build():
    market = json.loads((ROOT / 'marketplace.json').read_text())
    entry = market['plugins'][0]
    plugin = (ROOT / entry['source']).resolve()
    manifest = json.loads((plugin / '.zcode-plugin/plugin.json').read_text())
    if entry['name'] != manifest['name'] or entry['version'] != manifest['version']:
        raise ValueError('Marketplace and plugin identity/version differ')
    files = [ROOT / 'marketplace.json'] + sorted(p for p in (ROOT/'assets').rglob('*') if p.is_file()) + sorted(p for p in plugin.rglob('*') if p.is_file())
    for p in files:
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT):
            raise ValueError(f'Package file escapes source tree: {p}')
        if p.suffix not in {'.md', '.json', '.yaml', '.png', '.svg'}:
            raise ValueError(f'Unexpected package file: {p}')
    OUT.mkdir(exist_ok=True)
    target = OUT / f"routine-{manifest['version']}.zip"
    hashes = {}
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            rel = 'finam/' + p.relative_to(ROOT).as_posix()
            body = p.read_bytes()
            info = zipfile.ZipInfo(rel, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, body)
            hashes[rel] = hashlib.sha256(body).hexdigest()
    (OUT / 'package-files.json').write_text(json.dumps(hashes, indent=2) + '\n')
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (OUT / (target.name + '.sha256')).write_text(f'{digest}  {target.name}\n')
    print(f'{target}\n{len(files)} files; sha256 {digest}')
    return target

if __name__ == '__main__':
    build()
