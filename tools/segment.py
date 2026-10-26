import re,glob,os,json
PRE=re.compile(r'^(?:\s*\d+:)?(?:\[[^\]]*\]|\s)*')
SUF=re.compile(r'(?:\[[^\]]*\]|\s)*$')
def split_file(s):
    parts=s.split('[ENDN]')
    segs=[]
    for p in parts:
        m=PRE.match(p); pre=m.group(0); rest=p[len(pre):]
        m2=SUF.search(rest); suf=m2.group(0); body=rest[:len(rest)-len(suf)]
        segs.append((pre,body,suf))
    return segs
if __name__=='__main__':
    db={}   # body -> id
    files={}
    for p in sorted(glob.glob('orig/text/us/**/*',recursive=True)):
        if os.path.isdir(p) or p.endswith('warning'): continue
        rel=os.path.relpath(p,'orig/text/us').replace(os.sep,'/')
        s=open(p,encoding='utf-8').read()
        segs=split_file(s)
        assert '[ENDN]'.join(a+b+c for a,b,c in segs)==s
        ids=[]
        for a,b,c in segs:
            if b.strip()=='' : ids.append(None); continue
            if b not in db: db[b]=len(db)
            ids.append(db[b])
        files[rel]=[(a,i if i is not None else b,c) for (a,b,c),i in zip(segs,ids)]
    json.dump(files,open('segfiles.json','w',encoding='utf-8'),ensure_ascii=False)
    bodies=[None]*len(db)
    for b,i in db.items(): bodies[i]=b
    json.dump(bodies,open('bodies.json','w',encoding='utf-8'),ensure_ascii=False)
    print(len(bodies),sum(len(b) for b in bodies))
    # first-occurrence file per id
    first={}
    for rel,L in files.items():
        for a,i,c in L:
            if isinstance(i,int) and i not in first: first[i]=rel
    json.dump(first,open('firstfile.json','w'))
