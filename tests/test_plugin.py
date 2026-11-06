"""Development checks only. No dependency checks and no external operations."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/routine'

def frontmatter(path):
    text = path.read_text()
    match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not match:
        raise AssertionError(f'Missing frontmatter: {path}')
    return yaml.safe_load(match.group(1)), text[match.end():]

class PackageTests(unittest.TestCase):
    def test_marketplace_resolves_components(self):
        market = json.loads((ROOT/'marketplace.json').read_text())
        self.assertEqual(len(market['plugins']),1)
        entry = market['plugins'][0]
        self.assertEqual((ROOT/entry['source']).resolve(),PLUGIN)
        meta = json.loads((PLUGIN/'.zcode-plugin/plugin.json').read_text())
        self.assertEqual((entry['name'],entry['version']),(meta['name'],meta['version']))
        for field in ('commands',):
            self.assertTrue((PLUGIN/meta[field]).is_dir())
        for field in ('dependencies','hooks','mcpServers'):
            self.assertNotIn(field,meta)
        self.assertFalse((PLUGIN/'.mcp.json').exists())

    def test_command_discovery(self):
        meta=json.loads((PLUGIN/'.zcode-plugin/plugin.json').read_text())
        self.assertNotIn('skills',meta)
        self.assertFalse((PLUGIN/'skills').exists())
        commands=list((PLUGIN/'commands').glob('*.md'))
        self.assertEqual({p.stem for p in commands},{'routine','routine_setup'})
        for p in commands:
            fm,body=frontmatter(p)
            self.assertTrue(fm['description'])
            self.assertNotIn('skills',fm)
            self.assertIn('$ARGUMENTS',body)
            self.assertIn('.harness/routine/project.yaml',body)
            self.assertIn('../references/project-contract.md',body)

    def test_all_bundled_markdown_resources_resolve_inside_package(self):
        for p in PLUGIN.rglob('*.md'):
            for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if '://' in dest or dest.startswith('#') or '<' in dest:
                    continue
                target=(p.parent/dest.split('#')[0]).resolve()
                self.assertTrue(target.is_relative_to(PLUGIN), (p,dest))
                self.assertTrue(target.is_file(),(p,dest))

    def test_templates_and_review_selection(self):
        minimal=yaml.safe_load((PLUGIN/'templates/project.yaml').read_text())
        example=yaml.safe_load((PLUGIN/'templates/project.example.yaml').read_text())
        self.assertIsNone(minimal['review']['executor'])
        self.assertEqual(minimal['quality']['checks'],[])
        for d in [minimal,example]:
            self.assertEqual(d['schema_version'],1)
            self.assertNotIn('current_task',d)
            self.assertNotIn('current_branch',d)
        ids=set()
        for c in example['quality']['checks']:
            self.assertNotIn(c['id'],ids);ids.add(c['id'])
            for key in ('purpose','required_when','success','evidence'):
                self.assertTrue(c[key])
            x=c['execution']
            if x['kind']=='command':
                self.assertTrue(x['command']);self.assertTrue(x['cwd'])
            else:
                self.assertEqual(x['kind'],'manual');self.assertTrue(x['instructions_path'])
        executor=example['review']['executor']
        self.assertEqual(executor['invocation']['mode'],'delegate_instructions')
        self.assertNotEqual(executor['source'],'.zcode/commands/routine_review.md')

    def test_archive_is_relocatable_and_matches_sources(self):
        version=json.loads((PLUGIN/'.zcode-plugin/plugin.json').read_text())['version']
        archive=ROOT/f'dist/routine-{version}.zip'
        self.assertTrue(archive.exists(),'Run scripts/build_plugin.py first')
        with tempfile.TemporaryDirectory() as temp,zipfile.ZipFile(archive) as z:
            self.assertIsNone(z.testzip())
            for name in z.namelist():
                p=Path(name)
                self.assertFalse(p.is_absolute());self.assertNotIn('..',p.parts)
                relative=p.relative_to('finam')
                self.assertEqual(z.read(name),(ROOT/relative).read_bytes())
                self.assertTrue(relative==Path('marketplace.json') or relative.is_relative_to('plugins/routine') or relative.is_relative_to('assets'))
            z.extractall(temp)
            moved=Path(temp)/'finam'
            entry=json.loads((moved/'marketplace.json').read_text())['plugins'][0]
            self.assertTrue((moved/entry['source']/'.zcode-plugin/plugin.json').exists())

if __name__=='__main__':
    unittest.main(verbosity=2)
