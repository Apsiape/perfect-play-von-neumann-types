"""Package relative-path sources and audited finite verification; write LF hashes."""
from pathlib import Path
import argparse,hashlib,json,re,zipfile

ROOT=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verification-dir',default='run')
    a=parser.parse_args();p=ROOT/'paper';v=ROOT/'verification';run=(v/a.verification_dir).resolve()
    if run.parent!=v.resolve():parser.error('verification directory must be a direct child of verification/')
    visual=json.loads((v/'visual-review.json').read_text())
    results=json.loads((run/'results.json').read_text())
    portable=json.loads((v/'portability-check.json').read_text())
    build=json.loads((v/'evidence/build-summary.json').read_text())
    assert visual['status']=='PASS' and visual['pdf_sha256']==sha(p/'main.pdf')
    assert visual['pages_inspected']==list(range(1,visual['page_count']+1))
    assert build['status']=='PASS' and build['pdf_sha256']==sha(p/'main.pdf')
    assert build['warnings']==build['unresolved_references']==build['box_defects']==0
    assert results['status']=='PASS' and results['script_sha256']==sha(v/'check_type_ladder.py')
    assert portable['status']=='PASS' and portable['script_sha256']==sha(v/'check_type_ladder.py')
    excluded={'paper/main.pdf','paper/source.zip','paper/source-manifest.json','verification/SHA256SUMS'}
    payload=[f for f in ROOT.rglob('*') if f.is_file()
      and f.relative_to(ROOT).as_posix() not in excluded
      and '__pycache__' not in f.parts and f.suffix not in {'.pyc','.pyo'}]
    payload=sorted(set(payload),key=lambda f:f.relative_to(ROOT).as_posix())
    assert all(f.is_file() for f in payload)
    for f in payload:
        if f.suffix in {'.txt','.json'}:
            assert not re.search(r'(?<![A-Za-z0-9_])[A-Za-z]:[/\\]',f.read_text(encoding='utf-8')),f
    manifest={
      'status':'COMPLETED_PAPER_AND_PASSING_FINITE_VERIFICATION',
      'date':'2026-11-03','title':build['title'],'pages':visual['page_count'],
      'external_sources':json.loads((v/'provenance-input.json').read_text())['external_sources'],
      'payload_files':[record(f) for f in payload],'pdf':record(p/'main.pdf'),
      'zip_policy':'Relative-path sources and evidence plus this manifest; PDF and checksums are external.',
      'verification_scope':results['scope']}
    write(p/'source-manifest.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    archived=payload+[p/'source-manifest.json']
    with zipfile.ZipFile(p/'source.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(archived,key=lambda f:f.relative_to(ROOT).as_posix()):
            zi=zipfile.ZipInfo(f.relative_to(ROOT).as_posix(),date_time=(2026,11,3,0,0,0))
            zi.create_system=3;zi.external_attr=0o100644<<16;zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    checked=sorted(archived+[p/'source.zip',p/'main.pdf'],key=lambda f:f.relative_to(ROOT).as_posix())
    write(v/'SHA256SUMS',''.join(sha(f)+'  '+f.relative_to(ROOT).as_posix()+'\n' for f in checked))
    assert b'\r' not in (v/'SHA256SUMS').read_bytes()
    for line in (v/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1);assert sha(ROOT/name)==digest
    with zipfile.ZipFile(p/'source.zip') as z:
        assert z.testzip() is None
        for f in archived:assert z.read(f.relative_to(ROOT).as_posix())==f.read_bytes()
    print(json.dumps({'status':'PASS','payload_files':len(payload),'archive_members':len(archived),
      'checksum_entries':len(checked),'pages':visual['page_count'],'main_pdf_sha256':sha(p/'main.pdf'),
      'source_zip_sha256':sha(p/'source.zip'),'manifest_sha256':sha(p/'source-manifest.json'),
      'sha256sums_sha256':sha(v/'SHA256SUMS')},indent=2))
if __name__=='__main__':main()
