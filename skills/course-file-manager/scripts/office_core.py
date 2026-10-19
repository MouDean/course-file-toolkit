"""Small read-only OOXML utilities shared by the roster and audit commands."""
from __future__ import annotations

import hashlib
import posixpath
import re
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zipfile import ZipFile

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = {'s': S}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def text_runs(element: ET.Element | None) -> str:
    if element is None:
        return ''
    result = []
    for child in element:
        if child.tag == f'{{{S}}}t':
            result.append(child.text or '')
        elif child.tag == f'{{{S}}}r':
            result.extend(t.text or '' for t in child.findall('s:t', NS))
    return ''.join(result)


def shared_strings(z: ZipFile) -> list[str]:
    if 'xl/sharedStrings.xml' not in z.namelist():
        return []
    return [text_runs(si) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]


def worksheets(z: ZipFile) -> list[dict]:
    workbook = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    targets = {r.get('Id'): r.get('Target') for r in rels
               if r.get('TargetMode') != 'External'}
    result = []
    for sheet in workbook.findall('s:sheets/s:sheet', NS):
        target = targets.get(sheet.get(f'{{{R}}}id'))
        if not target:
            raise ValueError('Missing worksheet relationship')
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl', target))
        if not member.startswith('xl/') or '..' in member.split('/'):
            raise ValueError('Worksheet target is outside the workbook package')
        result.append({'name': sheet.get('name'), 'state': sheet.get('state', 'visible'),
                       'part': member, 'sheet_id': sheet.get('sheetId')})
    return result


def cell_value(cell: ET.Element, strings: list[str]) -> str:
    typ = cell.get('t')
    value = cell.find('s:v', NS)
    text = value.text if value is not None and value.text is not None else ''
    if typ == 's':
        try:
            return strings[int(text)]
        except (ValueError, IndexError):
            raise ValueError(f'Invalid shared-string reference at {cell.get("r")}') from None
    if typ == 'inlineStr':
        return text_runs(cell.find('s:is', NS))
    if typ == 'e':
        raise ValueError(f'Excel error at {cell.get("r")}: {text}')
    if typ in {'str', 'b', 'd'} or not text:
        return text
    # Preserve the exact numeric integer rather than round IDs through a float.
    try:
        number = Decimal(text)
        if not number.is_finite():
            raise ValueError(f'Non-finite numeric cell at {cell.get("r")}')
        rendered = format(number, 'f')
        return rendered.partition('.')[0] if number == number.to_integral_value() else rendered
    except InvalidOperation:
        raise ValueError(f'Invalid numeric cell at {cell.get("r")}') from None


def column_index(address: str) -> int:
    match = re.fullmatch(r'([A-Z]+)([1-9][0-9]*)', address or '')
    if not match:
        raise ValueError(f'Invalid cell address: {address!r}')
    result = 0
    for char in match[1]:
        result = result * 26 + ord(char) - 64
    return result


def xlsx_rows(path: Path, sheet_name: str | None = None) -> list[dict[int, str]]:
    with ZipFile(path) as z:
        sheets = worksheets(z)
        if sheet_name is None:
            selected = next((s for s in sheets if s['state'] == 'visible'), None)
        else:
            selected = next((s for s in sheets if s['name'] == sheet_name), None)
        if selected is None:
            raise ValueError('Requested worksheet was not found')
        strings = shared_strings(z)
        xml = ET.fromstring(z.read(selected['part']))
        rows = []
        # Read physical rows. Never use the possibly incorrect <dimension>.
        for row in xml.findall('s:sheetData/s:row', NS):
            values = {column_index(c.get('r')): cell_value(c, strings)
                      for c in row.findall('s:c', NS)}
            rows.append(values)
        return rows
