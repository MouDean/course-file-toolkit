"""Synthetic-only regression checks. No university files or accounts are read."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills' / 'course-file-manager' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import file_inventory
import office_audit
import roster_tools

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def workbook(path, headers=None, records=None, *, changed_style=False, formula='SUM(D2:D2)'):
    headers = headers or ['ID', 'Name']
    records = records if records is not None else [['0000123', "D'Example-Z,Alex Test"], ['TEST-0002', 'Exemple,Zoë Demo']]
    book = f'<workbook xmlns="{S}" xmlns:r="{R}"><sheets><sheet name="Roster" sheetId="1" r:id="rId1"/><sheet name="Cache" sheetId="2" state="veryHidden" r:id="rId2"/></sheets><definedNames><definedName name="ExampleRange">Roster!$A$1:$B$3</definedName></definedNames><calcPr calcId="1"/></workbook>'
    rels = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="/xl/worksheets/sheet2.xml"/></Relationships>'
    root = ET.Element('worksheet', xmlns=S)
    ET.SubElement(root, 'dimension', ref='A1')  # Intentionally wrong PeopleSoft-style extent.
    ET.SubElement(root, 'cols')
    data = ET.SubElement(root, 'sheetData')
    for i, values in enumerate([headers] + records, 1):
        row = ET.SubElement(data, 'row', r=str(i), ht='20')
        for j, value in enumerate(values):
            col = chr(65 + j)
            cell = ET.SubElement(row, 'c', r=f'{col}{i}', t='inlineStr', s='2' if changed_style and i == 2 and j == 0 else '1')
            ET.SubElement(ET.SubElement(cell, 'is'), 't').text = value
    # A separate formula cell must not become part of the ID/name data.
    row = ET.SubElement(data, 'row', r='8')
    cell = ET.SubElement(row, 'c', r='D8', s='1')
    ET.SubElement(cell, 'f').text = formula
    ET.SubElement(cell, 'v').text = '0'
    ET.SubElement(root, 'mergeCells')
    with ZipFile(path, 'w') as z:
        z.writestr('xl/workbook.xml', book)
        z.writestr('xl/_rels/workbook.xml.rels', rels)
        z.writestr('xl/worksheets/sheet1.xml', ET.tostring(root))
        z.writestr('xl/worksheets/sheet2.xml', f'<worksheet xmlns="{S}"><sheetData/></worksheet>')
        z.writestr('xl/styles.xml', '<styleSheet/>')
        z.writestr('xl/charts/chart1.xml', '<chart/>')


def document(path, section):
    w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    body = f'<w:document xmlns:w="{w}"><w:body><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Section #: </w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>{section}</w:t></w:r></w:p></w:body></w:document>'
    header = f'<w:hdr xmlns:w="{w}"><w:p><w:r><w:t>Example University</w:t></w:r></w:p></w:hdr>'
    with ZipFile(path, 'w') as z:
        z.writestr('word/document.xml', body)
        z.writestr('word/header1.xml', header)
        z.writestr('word/styles.xml', '<styles/>')


class Helpers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def normalize(self, path, count=2, **kwargs):
        return roster_tools.normalize(path, section='001', course='DEMO100', campus='EX', term='Example Term', class_number='CLASS_A', expected_count=count, **kwargs)

    def test_wrong_xlsx_dimension_and_leading_zero_ids(self):
        p = self.base / 'roster.xlsx'; workbook(p)
        doc = self.normalize(p)
        self.assertEqual(doc['count'], 2)
        self.assertEqual(doc['students'][0]['id'], '0000123')
        self.assertEqual(doc['students'][0]['last_name'], "D'Example-Z")
        self.assertEqual(doc['students'][1]['given_names'], 'Zoë Demo')
        self.assertFalse(doc['source']['identity_verified_by_helper'])

    def test_explicit_separate_name_headers(self):
        p = self.base / 'names.csv'
        p.write_text('Student ID,Last Name,First Name\n0001,Example Family,Alex Two Names\n', encoding='utf-8')
        doc = self.normalize(p, 1)
        self.assertEqual(doc['students'][0]['given_names'], 'Alex Two Names')
        self.assertEqual(doc['students'][0]['last_name'], 'Example Family')

    def test_shared_headers_and_numeric_integer_ids(self):
        original = self.base / 'original.xlsx'; changed = self.base / 'numeric.xlsx'
        workbook(original)
        ns = {'s': S}
        with ZipFile(original) as zin, ZipFile(changed, 'w') as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename == 'xl/worksheets/sheet1.xml':
                    xml = ET.fromstring(data)
                    for address, typ, value in [('A1', 's', '0'), ('A2', 'n', '1234567.0')]:
                        cell = xml.find(f'.//s:c[@r="{address}"]', ns)
                        for child in list(cell): cell.remove(child)
                        cell.set('t', typ)
                        ET.SubElement(cell, f'{{{S}}}v').text = value
                    data = ET.tostring(xml)
                zout.writestr(info, data)
            zout.writestr('xl/sharedStrings.xml', f'<sst xmlns="{S}"><si><t>ID</t></si></sst>')
        self.assertEqual(self.normalize(changed)['students'][0]['id'], '1234567')

    def test_tsv_and_nonenglish_explicit_headers(self):
        p = self.base / 'names.tsv'
        p.write_text('Identifiant\tNom complet\nTEST-0001\tExemple,Élève Démo\n', encoding='utf-8')
        doc = self.normalize(p, 1, id_header='Identifiant', name_header='Nom complet')
        self.assertEqual(doc['students'][0]['given_names'], 'Élève Démo')

    def test_duplicate_ids_rejected(self):
        p = self.base / 'roster.xlsx'
        workbook(p, records=[['TEST-1', 'Example,One'], ['TEST-1', 'Sample,Two']])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.normalize(p)

    def test_count_mismatch_rejected(self):
        p = self.base / 'roster.xlsx'; workbook(p)
        with self.assertRaisesRegex(ValueError, 'Portal count'):
            self.normalize(p, 3)

    def test_incomplete_rows_not_silently_discarded(self):
        p = self.base / 'roster.xlsx'
        workbook(p, records=[['TEST-1', 'Example,One'], ['', 'Sample,Two']])
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            self.normalize(p)

    def test_no_space_based_name_guessing(self):
        p = self.base / 'roster.xlsx'
        workbook(p, records=[['TEST-1', 'Alex Example']])
        with self.assertRaisesRegex(ValueError, 'no observed comma'):
            self.normalize(p, 1)

    def test_empty_enrolled_section(self):
        p = self.base / 'roster.xlsx'; workbook(p, records=[])
        self.assertEqual(self.normalize(p, 0)['students'], [])

    def test_compare_order_and_changed_names(self):
        p = self.base / 'roster.xlsx'; workbook(p)
        left = self.normalize(p)
        right = copy.deepcopy(left); right['students'].reverse()
        right['roster_sha256'] = __import__('hashlib').sha256(roster_tools.canonical(right['students'])).hexdigest()
        result = roster_tools.compare(left, right)
        self.assertTrue(result['equivalent_records']); self.assertFalse(result['same_order'])
        right['students'][0]['given_names'] = 'Changed Demo'
        right['roster_sha256'] = __import__('hashlib').sha256(roster_tools.canonical(right['students'])).hexdigest()
        self.assertFalse(roster_tools.compare(left, right)['equivalent_records'])

    def test_tampered_digest_and_wrong_class_rejected(self):
        p = self.base / 'roster.xlsx'; workbook(p)
        left = self.normalize(p); right = copy.deepcopy(left)
        right['students'][0]['id'] = 'CHANGED'
        with self.assertRaisesRegex(ValueError, 'digest'):
            roster_tools.compare(left, right)
        right = copy.deepcopy(left); right['identity']['section'] = '004'
        with self.assertRaisesRegex(ValueError, 'identities differ'):
            roster_tools.compare(left, right)

    def test_office_compare_identifies_cells_and_native_parts(self):
        a = self.base / 'before.xlsx'; b = self.base / 'after.xlsx'
        workbook(a); workbook(b, changed_style=True, formula='SUM(D2:D3)')
        before = office_audit.inspect(a); after = office_audit.inspect(b)
        self.assertEqual(before['sheets'][0]['actual_cell_count'], 7)
        self.assertEqual(before['sheets'][0]['declared_dimension'], 'A1')
        self.assertEqual(before['sheets'][1]['state'], 'veryHidden')
        result = office_audit.compare(before, after)
        self.assertEqual(result['sheets'][0]['changed_style_cells'], ['A2'])
        self.assertEqual(result['sheets'][0]['changed_formula_cells'], ['D8'])
        self.assertNotIn('xl/styles.xml', result['changed_parts'])
        self.assertNotIn('xl/charts/chart1.xml', result['changed_parts'])

    def test_docx_text_change_preserves_format_digests(self):
        a = self.base / 'before.docx'; b = self.base / 'after.docx'
        document(a, '001'); document(b, '004')
        before = office_audit.inspect(a); after = office_audit.inspect(b)
        self.assertNotEqual(before['stories']['word/document.xml']['text_sha256'], after['stories']['word/document.xml']['text_sha256'])
        self.assertEqual(before['stories']['word/document.xml']['run_properties_sha256'], after['stories']['word/document.xml']['run_properties_sha256'])
        self.assertEqual(office_audit.compare(before, after)['changed_parts'], ['word/document.xml'])

    def test_file_inventory_empty_folders_and_same_size_changes(self):
        a = self.base / 'template'; a.mkdir(); (a / 'empty').mkdir(); (a / 'one.txt').write_text('abc')
        b = self.base / 'copy'; shutil.copytree(a, b)
        original = file_inventory.inventory(a)
        self.assertTrue(file_inventory.differences(original, file_inventory.inventory(b))['exact_copy'])
        (b / 'one.txt').write_text('abd')
        self.assertEqual(file_inventory.differences(original, file_inventory.inventory(b))['changed_files'], ['one.txt'])
        (b / 'empty').rmdir()
        self.assertEqual(file_inventory.differences(original, file_inventory.inventory(b))['missing_folders'], ['empty'])

    def test_cli_refuses_report_overwrite(self):
        p = self.base / 'roster.xlsx'; workbook(p)
        out = self.base / 'existing.json'; out.write_text('do not replace', encoding='utf-8')
        command = [sys.executable, '-B', str(SCRIPTS / 'roster_tools.py'), 'normalize', str(p), '--section', '001', '--course', 'DEMO100', '--campus', 'EX', '--term', 'Example', '--class-number', 'CLASS_A', '--expected-count', '2', '--out', str(out)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(out.read_text(), 'do not replace')


if __name__ == '__main__':
    unittest.main()
