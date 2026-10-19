"""Read-only DOCX/XLSX structure reports and comparisons, without cell text."""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from office_core import NS, column_index, digest_bytes, file_digest, worksheets


def fingerprint(node: ET.Element | None) -> str | None:
    return digest_bytes(ET.tostring(node)) if node is not None else None


def inspect(path: Path) -> dict:
    if path.suffix.lower() not in {'.xlsx', '.docx'}:
        raise ValueError('This helper supports DOCX and XLSX only')
    with ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive member names require review')
        if z.testzip() is not None:
            raise ValueError('Archive integrity check failed')
        report = {'format': path.suffix.lower()[1:], 'sha256': file_digest(path),
                  'parts': {n: digest_bytes(z.read(n)) for n in names if not n.endswith('/')}}
        if path.suffix.lower() == '.docx':
            w = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            stories = {}
            for name in names:
                if name == 'word/document.xml' or (name.startswith(('word/header', 'word/footer')) and name.endswith('.xml')):
                    xml = ET.fromstring(z.read(name))
                    stories[name] = {'paragraph_count': len(xml.findall('.//w:p', w)),
                                     'table_count': len(xml.findall('.//w:tbl', w)),
                                     'text_run_count': len(xml.findall('.//w:t', w)),
                                     'text_sha256': digest_bytes(''.join(t.text or '' for t in xml.findall('.//w:t', w)).encode('utf-8')),
                                     'run_properties_sha256': digest_bytes(b''.join(ET.tostring(r) for r in xml.findall('.//w:rPr', w))),
                                     'paragraph_properties_sha256': digest_bytes(b''.join(ET.tostring(r) for r in xml.findall('.//w:pPr', w)))}
            report['stories'] = stories
            return report
        result = []
        workbook = ET.fromstring(z.read('xl/workbook.xml'))
        report['defined_names'] = {n.get('name') + ':' + n.get('localSheetId', '*'): digest_bytes((n.text or '').encode())
                                   for n in workbook.findall('s:definedNames/s:definedName', NS)}
        report['calculation_properties'] = dict(workbook.find('s:calcPr', NS).attrib) if workbook.find('s:calcPr', NS) is not None else None
        for sheet in worksheets(z):
            xml = ET.fromstring(z.read(sheet['part']))
            cells, max_row, max_col = {}, 0, 0
            for row in xml.findall('s:sheetData/s:row', NS):
                for cell in row.findall('s:c', NS):
                    address = cell.get('r')
                    f = cell.find('s:f', NS)
                    value_nodes = [c for c in cell if c.tag.rsplit('}', 1)[-1] in {'v', 'is'}]
                    cells[address] = {'style': cell.get('s'), 'type': cell.get('t'),
                                      'formula': fingerprint(f),
                                      'value': digest_bytes(b''.join(ET.tostring(c) for c in value_nodes))}
                    max_row = max(max_row, int(''.join(c for c in address if c.isdigit())))
                    max_col = max(max_col, column_index(address))
            dimension = xml.find('s:dimension', NS)
            result.append({**sheet, 'declared_dimension': dimension.get('ref') if dimension is not None else None,
                           'actual_cell_count': len(cells), 'max_physical_row': max_row, 'max_physical_column': max_col,
                           'formula_cell_count': sum(c['formula'] is not None for c in cells.values()),
                           'cells': cells,
                           'merges': [m.get('ref') for m in xml.findall('s:mergeCells/s:mergeCell', NS)],
                           'column_settings': fingerprint(xml.find('s:cols', NS)),
                           'row_properties': {r.get('r'): {k: v for k, v in r.attrib.items() if k != 'r'}
                                              for r in xml.findall('s:sheetData/s:row', NS)},
                           'validation': fingerprint(xml.find('s:dataValidations', NS)),
                           'conditional_formats': [fingerprint(c) for c in xml.findall('s:conditionalFormatting', NS)],
                           'sheet_protection': fingerprint(xml.find('s:sheetProtection', NS))})
        report['sheets'] = result
        return report


def compare(before: dict, after: dict) -> dict:
    if before['format'] != after['format']:
        raise ValueError('Cannot compare different Office formats')
    a, b = before['parts'], after['parts']
    changed = sorted(n for n in a.keys() & b.keys() if a[n] != b[n])
    result = {'identical_package_parts': a == b,
              'removed_parts': sorted(a.keys() - b.keys()), 'added_parts': sorted(b.keys() - a.keys()),
              'changed_parts': changed,
              'review_required': a != b}
    if before['format'] == 'docx':
        result['stories_before'] = before['stories']
        result['stories_after'] = after['stories']
        return result
    result['sheet_order_or_visibility_changed'] = [(s['name'], s['state']) for s in before['sheets']] != [(s['name'], s['state']) for s in after['sheets']]
    result['defined_names_changed'] = before['defined_names'] != after['defined_names']
    result['sheets'] = []
    by_name = {s['name']: s for s in after['sheets']}
    for old in before['sheets']:
        if old['name'] not in by_name:
            continue
        new = by_name[old['name']]
        ac, bc = old['cells'], new['cells']
        common = ac.keys() & bc.keys()
        result['sheets'].append({'name': old['name'],
            'added_cells': sorted(bc.keys() - ac.keys()), 'removed_cells': sorted(ac.keys() - bc.keys()),
            'changed_value_cells': sorted(c for c in common if ac[c]['value'] != bc[c]['value'] or ac[c]['type'] != bc[c]['type']),
            'changed_formula_cells': sorted(c for c in common if ac[c]['formula'] != bc[c]['formula']),
            'changed_style_cells': sorted(c for c in common if ac[c]['style'] != bc[c]['style']),
            'column_settings_changed': old['column_settings'] != new['column_settings'],
            'row_properties_changed': old['row_properties'] != new['row_properties'],
            'merges_changed': old['merges'] != new['merges'],
            'validation_changed': old['validation'] != new['validation'],
            'conditional_formats_changed': old['conditional_formats'] != new['conditional_formats'],
            'protection_changed': old['sheet_protection'] != new['sheet_protection']})
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    item = sub.add_parser('inspect')
    item.add_argument('file', type=Path)
    item.add_argument('--out', type=Path)
    item = sub.add_parser('compare')
    item.add_argument('before', type=Path)
    item.add_argument('after', type=Path)
    item.add_argument('--out', type=Path)
    args = p.parse_args()
    try:
        result = inspect(args.file) if args.command == 'inspect' else compare(inspect(args.before), inspect(args.after))
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2)
            print(json.dumps({'report_written': True, 'format': result.get('format'),
                              'review_required': result.get('review_required')}))
        else:
            print(json.dumps(result, indent=2))
        return 0  # A diff report is not an automatic approval/failure decision.
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
