"""Inventory actual files and empty folders; compare a copy to that inventory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from office_core import file_digest


def inventory(root: Path) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Root must be a folder')
    def walk(folder):
        for entry in sorted(folder.iterdir()):
            if entry.is_symlink() or (hasattr(entry, 'is_junction') and entry.is_junction()):
                raise ValueError(f'Linked path needs separate review: {entry.relative_to(root)}')
            yield entry
            if entry.is_dir():
                yield from walk(entry)
    files, folders = {}, []
    for entry in walk(root):
        relative = entry.relative_to(root).as_posix()
        if entry.is_dir():
            folders.append(relative)
        elif entry.is_file():
            before = entry.stat()
            digest = file_digest(entry)
            after = entry.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError(f'File changed while reading: {relative}')
            files[relative] = {'bytes': after.st_size, 'sha256': digest}
        else:
            raise ValueError(f'Unsupported filesystem entry: {relative}')
    return {'schema_version': 1, 'folders': folders, 'files': files,
            'file_count': len(files), 'folder_count': len(folders),
            'total_bytes': sum(f['bytes'] for f in files.values())}


def differences(before: dict, after: dict) -> dict:
    a, b = before['files'], after['files']
    result = {'missing_files': sorted(a.keys() - b.keys()), 'extra_files': sorted(b.keys() - a.keys()),
              'changed_files': sorted(n for n in a.keys() & b.keys() if a[n] != b[n]),
              'missing_folders': sorted(set(before['folders']) - set(after['folders'])),
              'extra_folders': sorted(set(after['folders']) - set(before['folders']))}
    return {'exact_copy': not any(result.values()), **result}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder', type=Path)
    group = p.add_mutually_exclusive_group()
    group.add_argument('--out', type=Path, help='New report path outside the inventoried folder')
    group.add_argument('--compare', type=Path, help='Existing template inventory')
    args = p.parse_args()
    try:
        if args.out:
            root = args.folder.resolve(strict=True)
            if args.out.resolve().is_relative_to(root):
                raise ValueError('Write the inventory outside the folder being inventoried')
        actual = inventory(args.folder)
        if args.compare:
            result = differences(json.loads(args.compare.read_text(encoding='utf-8')), actual)
            print(json.dumps(result, indent=2))
            return 0 if result['exact_copy'] else 1
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open('x', encoding='utf-8') as stream:
                json.dump(actual, stream, indent=2)
        print(json.dumps({k: actual[k] for k in ['file_count', 'folder_count', 'total_bytes']}))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
