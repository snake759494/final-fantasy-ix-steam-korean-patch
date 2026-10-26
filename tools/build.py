"""FF9 한글패치 빌드: python build.py [x64|x86|all]"""
import UnityPy, json, re, os, sys, glob, math, shutil
from fontTools.ttLib import TTFont

W = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(W)
BACKUP = os.path.join(GAME, '_original_backup')
TAG = re.compile(r'\[[^\]]*\]')
VAR_TAGS = re.compile(r'\[(ZDNE|VIVI|DGGR|STNR|FRYA|QUIN|EIKO|AMRT|PTY\d?|CHR\d?)\]|\[(ITEM|NUMB|TEXT)=[^\]]*\]')

_f = TTFont(os.path.join(W, 'font', 'merged.ttf'))
_cmap = _f.getBestCmap(); _hm = _f['hmtx'].metrics


def em(s):
    s = VAR_TAGS.sub('XXXXXX', s)
    s = TAG.sub('', s)
    return sum(_hm[_cmap[ord(c)]][0] if ord(c) in _cmap else 1000 for c in s) / 1000


def maxline(s):
    return max(em(l) for l in s.split('\n'))


def load_trans():
    ko = {}
    for p in glob.glob(os.path.join(W, 'trans', 'out', '*.json')):
        if '.part' in p:
            continue
        for k, v in json.load(open(p, encoding='utf-8')).items():
            ko[int(k)] = v
    return ko


STRT = re.compile(r'\[STRT=(\d+),(\d+)\]')


OVERRIDE = {'item/': {'Dagger': '대거'}}


def rebuild(segs, bodies, ko, rel=''):
    over = {}
    for pfx, m in OVERRIDE.items():
        if rel.startswith(pfx):
            over = m
    out = []
    for pre, i, suf in segs:
        if not isinstance(i, int):
            out.append(pre + i + suf); continue
        en = bodies[i]; tr = over.get(en, ko.get(i, en))
        m = STRT.search(pre)
        if m and tr != en:
            w0, l0 = int(m.group(1)), int(m.group(2))
            if w0 > 0 and w0 >= 0.6 * 9.82 * maxline(en):
                w = w0 + 9.82 * (maxline(tr) - maxline(en))
                w = max(int(math.ceil(w)) + 4, int(math.ceil(9.82 * maxline(tr))) + 2)
            else:
                w = w0
            l = max(1, l0 + tr.count('\n') - en.count('\n'))
            pre = pre[:m.start()] + '[STRT=%d,%d]' % (w, l) + pre[m.end():]
        out.append(pre + tr + suf)
    return '[ENDN]'.join(out)


def build_texts():
    bodies = json.load(open(os.path.join(W, 'bodies.json'), encoding='utf-8'))
    files = json.load(open(os.path.join(W, 'segfiles.json'), encoding='utf-8'))
    ko = load_trans()
    res = {}
    for rel, segs in files.items():
        res['embeddedasset/text/us/' + rel] = rebuild(segs, bodies, ko, rel)
    extra = os.path.join(W, 'trans', 'extra')   # 수동 번역 파일(경고문, localization 등)
    for p in glob.glob(os.path.join(extra, '**', '*'), recursive=True):
        if os.path.isfile(p):
            res['embeddedasset/' + os.path.relpath(p, extra).replace(os.sep, '/')] = open(p, encoding='utf-8').read()
    return res


def encrypt(b):
    return b[1024:2048] + b[1024:] + b[:1024]


def patch(arch):
    data_dir = os.path.join(GAME, arch, 'FF9_Data')
    bdir = os.path.join(BACKUP, arch, 'FF9_Data')
    os.makedirs(bdir, exist_ok=True)
    for fn in ['resources.assets', 'sharedassets2.assets', 'sharedassets3.assets', 'sharedassets1.assets']:
        if not os.path.exists(os.path.join(bdir, fn)):
            shutil.copy2(os.path.join(data_dir, fn), os.path.join(bdir, fn))
    cont = json.load(open(os.path.join(W, 'data', 'container.json')))
    bypid = {pid: k for k, f, pid in cont if f == 5}
    texts = build_texts()
    font = encrypt(open(os.path.join(W, 'font', 'p_fa_new.bundle'), 'rb').read())
    env = UnityPy.load(os.path.join(bdir, 'resources.assets'))
    n = 0
    for o in env.objects:
        if o.type.name != 'TextAsset' or o.path_id not in bypid:
            continue
        k = bypid[o.path_id]
        if k in texts or k == 'embeddedasset/fa/p_fa.mpc':
            d = o.read()
            new = font if k.endswith('p_fa.mpc') else texts[k].encode('utf-8')
            d.m_Script = new.decode('utf-8', 'surrogateescape')
            d.save(); n += 1
    out = env.file.save()
    open(os.path.join(data_dir, 'resources.assets'), 'wb').write(out)
    print(arch, 'resources.assets 교체 항목', n)
    import images
    images.patch(arch, bdir, data_dir)


if __name__ == '__main__':
    arch = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for a in (['x64', 'x86'] if arch == 'all' else [arch]):
        patch(a)
