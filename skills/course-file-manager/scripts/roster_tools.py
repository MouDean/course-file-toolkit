"""Normalize identified CSV/XLSX exports and compare complete roster records.

This utility does not verify that the caller chose the correct portal class.
Section identity and expected count must come from independent source evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from office_core import file_digest, xlsx_rows


def label(value: str) -> str:
    return re.sub(r'[^\w]', '', value.casefold())


def read_rows(path: Path, sheet: str | None, encoding: str) -> list[dict[int, str]]:
    if path.suffix.lower() == '.xlsx':
        return xlsx_rows(path, sheet)
    if path.suffix.lower() not in {'.csv', '.tsv'}:
        raise ValueError('Use XLSX, CSV, or TSV; legacy XLS must be exported as XLSX/CSV')
    text = path.read_text(encoding=encoding)
    if path.suffix.lower() == '.tsv':
        reader = csv.reader(io.StringIO(text), delimiter='\t')
    else:
        try:
            dialect = csv.Sniffer().sniff(text[:8192], delimiters=',;\t')
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(io.StringIO(text), dialect=dialect)
    return [{i + 1: value for i, value in enumerate(row)} for row in reader]


def canonical(students: list[dict]) -> bytes:
    records = [{'id': s['id'], 'name': s['name'], 'last_name': s.get('last_name'),
                'given_names': s.get('given_names')} for s in students]
    return json.dumps(records, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def normalize(path: Path, *, section: str, course: str, campus: str, term: str,
              class_number: str, expected_count: int, sheet: str | None = None,
              encoding: str = 'utf-8-sig', id_header: str | None = None,
              name_header: str | None = None, last_header: str | None = None,
              given_header: str | None = None) -> dict:
    if expected_count < 0:
        raise ValueError('Expected count must be nonnegative')
    if not all(str(v).strip() for v in [section, course, campus, term, class_number]):
        raise ValueError('Course, term, campus, section and class number are required')
    rows = read_rows(path, sheet, encoding)
    aliases = {
        'id': {label(id_header)} if id_header else {'id', 'studentid', 'studentnumber', 'studentno', 'emplid'},
        'name': {label(name_header)} if name_header else {'name', 'studentname', 'fullname'},
        'last': {label(last_header)} if last_header else {'lastname', 'surname', 'familyname'},
        'given': {label(given_header)} if given_header else {'firstname', 'givenname', 'givennames'},
    }
    header = None
    for index, row in enumerate(rows[:100]):
        mapping = {}
        for key, names in aliases.items():
            matches = [col for col, value in row.items() if label(value.strip()) in names]
            if len(matches) > 1:
                continue
            if matches:
                mapping[key] = matches[0]
        if 'id' in mapping and ('name' in mapping or {'last', 'given'} <= mapping.keys()):
            header = index, mapping
            break
    if header is None:
        raise ValueError('No unambiguous ID/name header found; specify exact header options or select the correct sheet')
    index, mapping = header
    students, seen = [], set()
    for number, row in enumerate(rows[index + 1:], index + 2):
        sid = row.get(mapping['id'], '').strip()
        raw = row.get(mapping.get('name'), '').strip()
        last = row.get(mapping.get('last'), '').strip()
        given = row.get(mapping.get('given'), '').strip()
        if not any([sid, raw, last, given]):
            continue
        if not sid or not any([raw, last, given]):
            raise ValueError(f'Incomplete student row {number}; do not silently discard it')
        if sid in seen:
            raise ValueError(f'Duplicate student ID on row {number}')
        seen.add(sid)
        if not {'last', 'given'} <= mapping.keys():
            if ',' not in raw:
                raise ValueError(f'Name on row {number} has no observed comma split; provide separate name columns rather than guessing')
            last, given = [part.strip() for part in raw.split(',', 1)]
        if not raw:
            raw = f'{last},{given}'
        if not last or not given:
            raise ValueError(f'Empty surname or given-name component on row {number}; obtain an explicit mapping')
        students.append({'id': sid, 'name': raw, 'last_name': last, 'given_names': given})
    if len(students) != expected_count:
        raise ValueError(f'Portal count {expected_count} differs from export count {len(students)}')
    return {
        'schema_version': 1,
        'identity': {'course': course, 'term': term, 'campus': campus,
                     'section': section, 'class_number': class_number},
        'source': {'filename': path.name, 'sha256': file_digest(path),
                   'captured_at_utc': datetime.now(timezone.utc).isoformat(),
                   'identity_verified_by_helper': False},
        'count': len(students), 'expected_count': expected_count,
        'roster_sha256': hashlib.sha256(canonical(students)).hexdigest(), 'students': students,
    }


def validate_document(doc: dict) -> None:
    students = doc['students']
    if doc['count'] != len(students) or doc['expected_count'] != len(students):
        raise ValueError('Stored roster counts are inconsistent')
    if len({s['id'] for s in students}) != len(students):
        raise ValueError('Stored roster contains duplicate IDs')
    actual = hashlib.sha256(canonical(students)).hexdigest()
    if doc['roster_sha256'] != actual:
        raise ValueError('Stored roster digest does not match its records')


def compare(left: dict, right: dict) -> dict:
    validate_document(left)
    validate_document(right)
    if left['identity'] != right['identity']:
        raise ValueError('Roster identities differ; do not compare different classes as equivalent')
    a = {s['id']: s for s in left['students']}
    b = {s['id']: s for s in right['students']}
    common = a.keys() & b.keys()
    changed = sum(canonical([a[sid]]) != canonical([b[sid]]) for sid in common)
    equal = a.keys() == b.keys() and changed == 0
    return {'equivalent_records': equal, 'same_order': canonical(left['students']) == canonical(right['students']),
            'left_count': len(a), 'right_count': len(b), 'missing_count': len(a.keys() - b.keys()),
            'extra_count': len(b.keys() - a.keys()), 'changed_name_count': changed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('normalize', help='Normalize one identity-verified export')
    p.add_argument('export', type=Path)
    for key in ['section', 'course', 'campus', 'term', 'class-number']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--expected-count', type=int, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sheet')
    p.add_argument('--encoding', default='utf-8-sig')
    for key in ['id-header', 'name-header', 'last-header', 'given-header']:
        p.add_argument('--' + key)
    p = sub.add_parser('compare', help='Compare all normalized records without exposing IDs')
    p.add_argument('left', type=Path)
    p.add_argument('right', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'normalize':
            result = normalize(args.export, **{key: getattr(args, key) for key in
                ['section', 'course', 'campus', 'term', 'class_number', 'expected_count', 'sheet',
                 'encoding', 'id_header', 'name_header', 'last_header', 'given_header']})
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
            print(json.dumps({'section': args.section, 'count': result['count'],
                              'roster_sha256': result['roster_sha256']}))
            return 0
        result = compare(json.loads(args.left.read_text(encoding='utf-8')),
                         json.loads(args.right.read_text(encoding='utf-8')))
        print(json.dumps(result))
        return 0 if result['equivalent_records'] else 1
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
