import json, re, sys, os, collections
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
TAG = re.compile(r'\[[^\]]*\]')
HANGUL = re.compile(r'[가-힣]')


def vis_width(s):
    s = TAG.sub('', s)
    w = 0
    for ch in s:
        w += 1 if ord(ch) > 0x2000 else 0.5
    return w


def check(name):
    src = json.load(open(os.path.join(D, 'in', name + '.json'), encoding='utf-8'))
    p = os.path.join(D, 'out', name + '.json')
    if not os.path.exists(p):
        print('출력 파일 없음:', p); return 1
    out = json.load(open(p, encoding='utf-8'))
    errs = 0
    for i, en in src:
        ko = out.get(str(i))
        if ko is None:
            print(f'[누락] {i}'); errs += 1; continue
        if collections.Counter(TAG.findall(en)) != collections.Counter(TAG.findall(ko)):
            print(f'[태그 불일치] {i}: 원문 {TAG.findall(en)} / 번역 {TAG.findall(ko)}'); errs += 1
        if en.count('\n') != ko.count('\n') and ('[CHOO]' in en or '[MOVE' in en or '[XTAB' in en):
            print(f'[선택지 줄 수 불일치] {i}'); errs += 1
        for line in ko.split('\n'):
            if vis_width(line) > 24:
                print(f'[줄 너무 김 {vis_width(line)}] {i}: {line}'); errs += 1
        if re.search(r'[A-Za-z]{4,}', TAG.sub('', ko)) and not HANGUL.search(ko) and HANGUL.search(TAG.sub('', ko)) is None and len(TAG.sub('', en).strip()) > 0:
            pass
    extra = set(out) - {str(i) for i, _ in src}
    if extra:
        print('[불필요 id]', list(extra)[:10]); errs += 1
    print(f'{name}: 오류 {errs}개 / 항목 {len(src)}')
    return errs


if __name__ == '__main__':
    sys.exit(1 if check(sys.argv[1]) else 0)
