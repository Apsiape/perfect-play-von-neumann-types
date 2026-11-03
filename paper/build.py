"""Fresh pdflatex/BibTeX build; reject warnings and box defects."""
from pathlib import Path
import argparse,subprocess,shutil,re,sys,tempfile
p=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build-dir',default=None,help='new or empty build directory; default: a new system temporary directory')
a=parser.parse_args();b=(p/a.build_dir).resolve() if a.build_dir else Path(tempfile.mkdtemp(prefix='perfect-play-build-')).resolve()
if b==p:parser.error('build directory must differ from the paper source directory')
if b.exists() and any(b.iterdir()):parser.error('build directory must be new or empty')
b.mkdir(parents=True,exist_ok=True)
def run(args,name):
 r=subprocess.run(args,cwd=p,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (b/name).write_text(r.stdout,encoding='utf-8',newline='\n')
 if r.returncode:print(r.stdout[-8000:]);sys.exit(r.returncode)
tex=['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(b),'main.tex']
run(tex,'pdflatex-1.stdout')
run(['bibtex',str(b/'main')],'bibtex.stdout')
for i in range(2,5):run(tex,'pdflatex-'+str(i)+'.stdout')
log=(b/'main.log').read_text(errors='replace')
bad=[l for l in log.splitlines() if re.search(r'Warning:|Overfull|Underfull|undefined references|undefined citations',l,re.I)]
blg=(b/'main.blg').read_text(errors='replace')
bad += [l for l in blg.splitlines() if 'Warning--' in l or 'error message' in l.lower()]
if bad:print('FINAL BUILD ISSUES:\n'+'\n'.join(bad));sys.exit(2)
shutil.copy2(b/'main.pdf',p/'main.pdf')
print('Clean pdflatex + BibTeX build; zero warnings, unresolved references, overfull or underfull boxes.')
