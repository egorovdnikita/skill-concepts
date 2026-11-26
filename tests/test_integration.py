import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]

class IntegrationTests(unittest.TestCase):
    def test_two_directions_conflict_and_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); repo = base/'repo'; repo.mkdir(); remote = base/'remote.git'
            home = base/'home'; home.mkdir(); env = dict(os.environ, HOME=str(home))
            def cmd(*args, ok=True):
                r = subprocess.run(args, cwd=repo, env=env, capture_output=True, text=True)
                if ok:self.assertEqual(r.returncode,0,r.stderr)
                return r
            cmd('git','init','--bare',str(remote));cmd('git','init','-b','main')
            cmd('git','config','user.name','Никита Егоров');cmd('git','config','user.email','egorov.d.nikita@mail.ru')
            (repo/'scripts').mkdir();shutil.copyfile(SOURCE/'scripts/sync-skills.py',repo/'scripts/sync-skills.py')
            mirrors={}
            for name,path in [('concepts','SKILL.md'),('database','skills/database/SKILL.md')]:
                p=repo/path;p.parent.mkdir(parents=True,exist_ok=True)
                data=f'---\nname: {name}\ndescription: test\n---\nbase\n';p.write_text(data)
                m=home/f'.claude/skills/synced/bucket/{name}/SKILL.md';m.parent.mkdir(parents=True);m.write_text(data);mirrors[name]=m
            cmd('git','add','.');cmd('git','commit','-m','База теста');cmd('git','remote','add','origin',str(remote));cmd('git','push','origin','main')
            script=str(repo/'scripts/sync-skills.py')
            cmd('python3','-I',script,'init')
            # Изменение в ChatGPT уходит в зеркало и в remote.
            canonical=repo/'SKILL.md';canonical.write_text(canonical.read_text()+'local edit\n')
            cmd('python3','-I',script,'sync');self.assertEqual(canonical.read_bytes(),mirrors['concepts'].read_bytes())
            expected=cmd('git','rev-parse','HEAD').stdout.strip()
            self.assertEqual(cmd('git','--git-dir',str(remote),'rev-parse','main').stdout.strip(),expected)
            # Изменение synced из Claude импортируется в общий файл и git.
            mirror=mirrors['database'];mirror.write_text(mirror.read_text()+'cloud edit\n')
            cmd('python3','-I',script,'sync');self.assertEqual((repo/'skills/database/SKILL.md').read_bytes(),mirror.read_bytes())
            # Две разные правки не перезаписываются.
            canonical.write_text(canonical.read_text()+'local conflict\n');mirrors['concepts'].write_text(mirrors['concepts'].read_text()+'cloud conflict\n')
            a,b=canonical.read_bytes(),mirrors['concepts'].read_bytes()
            self.assertNotEqual(cmd('python3','-I',script,'sync',ok=False).returncode,0)
            self.assertEqual((a,b),(canonical.read_bytes(),mirrors['concepts'].read_bytes()))
            # Сбой отправки не выдаётся за успех; повтор сохраняет и отправляет правку.
            mirrors['concepts'].write_bytes(a)
            cmd('git','remote','set-url','--push','origin',str(base/'missing.git'))
            self.assertNotEqual(cmd('python3','-I',script,'sync',ok=False).returncode,0)
            cmd('git','remote','set-url','--push','origin',str(remote))
            cmd('python3','-I',script,'sync')
            self.assertEqual(cmd('git','rev-parse','HEAD').stdout.strip(),cmd('git','--git-dir',str(remote),'rev-parse','main').stdout.strip())

if __name__=='__main__':unittest.main()
