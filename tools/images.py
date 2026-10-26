"""텍스처(이미지) 한글화: 원본 스프라이트 영역을 지우고 직접 그린 한글로 교체"""
import os, json
import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(W)
SERIF_EB = os.path.join(GAME, 'SeoulHangangEB.ttf')
SERIF_B = os.path.join(GAME, 'SeoulHangangB.ttf')
SERIF_M = os.path.join(GAME, 'SeoulHangangM.ttf')
GOTHIC = os.path.join(GAME, 'NanumSquareNeo-cBd.ttf')
GOTHIC_EB = os.path.join(GAME, 'NanumSquareNeo-dEb.ttf')

ATLAS = json.load(open(os.path.join(W, 'data', 'atlases.json')))


def fit_font(path, text, w, h, maxsize=None):
    size = maxsize or h
    while size > 6:
        f = ImageFont.truetype(path, size)
        b = ImageDraw.Draw(Image.new('L', (1, 1))).multiline_textbbox((0, 0), text, font=f, spacing=size * 0.15)
        if b[2] - b[0] <= w and b[3] - b[1] <= h:
            return f, b
        size -= 1
    return f, b


def render(text, w, h, style, align='left'):
    """w×h RGBA 이미지에 스타일대로 한글을 그린다"""
    S = 4  # 슈퍼샘플링
    pad = {'gold': 0.03, 'glow': 0.08, 'plain': 0.02, 'white': 0.05}[style]
    font_path = {'gold': SERIF_EB, 'glow': SERIF_M, 'plain': GOTHIC_EB, 'white': SERIF_B}[style]
    iw, ih = int(w * (1 - pad * 2) * S), int(h * (1 - pad * 2) * S)
    f, b = fit_font(font_path, text, iw, ih)
    tw, th = b[2] - b[0], b[3] - b[1]
    W_, H_ = w * S, h * S
    if align == 'left':
        ox = int(w * pad * S) - b[0]
    else:
        ox = (W_ - tw) // 2 - b[0]
    oy = (H_ - th) // 2 - b[1]
    mask = Image.new('L', (W_, H_), 0)
    ImageDraw.Draw(mask).multiline_text((ox, oy), text, font=f, fill=255, spacing=f.size * 0.15, align='center' if align != 'left' else 'left')
    out = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    if style == 'gold':
        # 위: 크림색 → 아래: 주황 갈색 그라데이션, 어두운 테두리 + 그림자
        y = np.linspace(0, 1, H_)[:, None]
        top, bot = np.array([255, 246, 222]), np.array([214, 120, 58])
        grad = (top * (1 - y)[..., None] + bot * y[..., None]).astype(np.uint8)
        grad = np.broadcast_to(grad, (H_, W_, 3))
        stroke = mask.filter(ImageFilter.MaxFilter(2 * (S + 1) + 1))
        shadow = stroke.filter(ImageFilter.GaussianBlur(S * 2))
        out.paste((20, 8, 0, 200), (0, 0), shadow)
        out.paste((70, 30, 10, 255), (0, 0), stroke)
        fill = Image.fromarray(np.ascontiguousarray(grad), 'RGB').convert('RGBA')
        out.paste(fill, (0, 0), mask)
    elif style == 'glow':
        glow = mask.filter(ImageFilter.GaussianBlur(S * 5))
        g = Image.new('RGBA', (W_, H_), (255, 214, 160, 0)); g.putalpha(glow.point(lambda v: min(255, v * 2)))
        out.alpha_composite(g)
        out.paste((255, 252, 245, 255), (0, 0), mask)
    elif style == 'plain':
        stroke = mask.filter(ImageFilter.MaxFilter(2 * S + 1))
        out.paste((30, 30, 30, 230), (0, 0), stroke)
        out.paste((222, 222, 210, 255), (0, 0), mask)
    elif style == 'white':
        sh = mask.filter(ImageFilter.GaussianBlur(S * 2))
        out.paste((0, 0, 0, 220), (S * 2, S * 2), sh)
        out.paste((255, 255, 255, 255), (0, 0), mask)
    return out.resize((w, h), Image.LANCZOS)


# (아틀라스 키, 스프라이트, 한글, 스타일, 정렬, 왼쪽 보존 폭)
GENERAL = [
    ('title_menu_continue', '이어하기', 'gold', 'left', 0),
    ('title_menu_newgame', '새로 시작', 'gold', 'left', 0),
    ('title_menu_loadgame', '불러오기', 'gold', 'left', 0),
    ('title_menu_cloud', '클라우드 데이터', 'gold', 'left', 0),
    ('title_language_01', '한국어', 'gold', 'left', 0),
    ('title_back_01', '돌아가기', 'gold', 'left', 40),
    ('title_info_04', '정보', 'gold', 'left', 0),
    ('pause_us_uk_jp_fr_gr', '일시정지', 'gold', 'center', 0),
    ('text_levelup_us_uk_jp_gr_it', '레벨 업!', 'gold', 'center', 0),
    ('name_header_us_uk_jp_gr', '이름', 'gold', 'center', 0),
    ('caption_help_us_uk_jp', '도움말', 'plain', 'center', 0),
    ('text_poison_us_uk_jp_fr', '독', 'plain', 'center', 0),
    ('text_stone_us_uk_jp', '석화', 'plain', 'center', 0),
    ('ate_selective_text00_01_us_uk', '누르면', 'plain', 'center', 0),
    ('ate_selective_text00_02_us_uk', 'ATE 보기', 'plain', 'center', 0),
]
HEADERS = [  # 양옆 장식선이 있는 제목
    ('title_language_header_01', '언어 선택'),
    ('title_movie_01', '무비 갤러리'),
]
TUTORIAL = [
    ('tutorial_help_02_us', '캐릭터를 탭', 'plain', 'left', 0),
    ('tutorial_help_pc_02_us_uk', '캐릭터를 클릭', 'plain', 'left', 0),
]
# 엔딩 자막 번역문은 번역 대본에 해당하므로 저장소에 넣지 않음:
# trans/image_text.json = {"ending_text_01_us": "...", ..., "ending_text_07_bg_us": "..."}
_IT = os.path.join(W, 'trans', 'image_text.json')
ENDING = list(json.load(open(_IT, encoding='utf-8')).items()) if os.path.exists(_IT) else []


def sprite(key, name):
    for s in ATLAS[key]:
        if s[0] == name:
            return s[1:]
    raise KeyError(name)


def put(img, rect, new, keep_left=0):
    x, y, w, h = rect
    region = img.crop((x, y, x + w, y + h))
    blank = Image.new('RGBA', (w - keep_left, h), (0, 0, 0, 0))
    region.paste(blank, (keep_left, 0))
    region.alpha_composite(new.resize((w - keep_left, h)) if new.size != (w - keep_left, h) else new, (keep_left, 0))
    img.paste(region, (x, y))


def header(img, rect, text):
    x, y, w, h = rect
    new = render(text, int(w * 0.5), h, 'gold', 'center')
    a = np.array(new)[..., 3]
    cols = np.where(a.max(axis=0) > 40)[0]
    tl, tr = cols.min() + (w - new.width) // 2, cols.max() + (w - new.width) // 2
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    S = 4
    big = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    cy = h * S // 2
    for (x0, x1, fade_left) in [(int(w * 0.02), tl - 18, True), (tr + 18, int(w * 0.98), False)]:
        for i in range(x0 * S, x1 * S):
            t = (i - x0 * S) / max(1, (x1 - x0) * S)
            al = int(255 * (t if fade_left else 1 - t))
            d.line([(i, cy - S), (i, cy + S)], fill=(255, 226, 190, al))
    canvas.alpha_composite(big.resize((w, h), Image.LANCZOS))
    canvas.alpha_composite(new, ((w - new.width) // 2, 0))
    img.paste(canvas, (x, y))


def edit_texture(tex, fn):
    img = tex.image.convert('RGBA')
    fn(img)
    tex.set_image(img)
    tex.save()


def patch(arch, bdir, data_dir):
    env = UnityPy.load(os.path.join(bdir, 'sharedassets2.assets'))
    for o in env.objects:
        if o.type.name != 'Texture2D':
            continue
        n = o.peek_name()
        tex = None
        if n == 'General Atlas':
            def fn(img):
                for name, t, st, al, kl in GENERAL:
                    r = sprite('sharedassets2.assets:General Atlas', name)
                    put(img, r, render(t, r[2] - kl, r[3], st, al), kl)
                for name, t in HEADERS:
                    header(img, sprite('sharedassets2.assets:General Atlas', name), t)
        elif n == 'TutorialUI Atlas':
            def fn(img):
                for name, t, st, al, kl in TUTORIAL:
                    r = sprite('sharedassets2.assets:TutorialUI Atlas', name)
                    put(img, r, render(t, r[2], r[3], st, al))
        elif n == 'Ending Text US JP GR Atlas':
            def fn(img):
                for name, t in ENDING:
                    r = sprite('sharedassets2.assets:Ending_Text_US_JP_GR_Atlas', name)
                    new = render(t, r[2], r[3], 'glow', 'left')
                    if name.endswith('bg_us'):
                        new = new.filter(ImageFilter.GaussianBlur(6))
                    put(img, r, new)
        elif n == 'title_image_00_text0':
            def fn(img):
                w, h = img.size
                img.paste(Image.new('RGBA', (w, h), (0, 0, 0, 0)), (0, 0))
                img.alpha_composite(render('미덕', w // 3, h // 2, 'white', 'center'), (w * 9 // 16, h // 4))
        elif n == 'title_image_00_text1':
            def fn(img):
                w, h = img.size
                img.paste(Image.new('RGBA', (w, h), (0, 0, 0, 0)), (0, 0))
                img.alpha_composite(render('누군가를 돕는 데\n이유가 필요해?', w // 2, int(h * 0.7), 'white', 'left'), (w // 20, h // 8))
        elif n in ('title_world_mist_us', 'title_world_mist_shadow_us'):
            def fn(img, n=n):
                w, h = img.size
                img.paste(Image.new('RGBA', (w, h), (0, 0, 0, 0)), (0, 0))
                t = render('안개 대륙', w * 5 // 8, h, 'white', 'center')
                if 'shadow' in n:
                    a = t.split()[3].filter(ImageFilter.GaussianBlur(4))
                    t = Image.new('RGBA', t.size, (0, 0, 0, 0)); t.putalpha(a)
                img.alpha_composite(t, (w * 5 // 16, 0))
        else:
            continue
        edit_texture(o.read(), fn)
        print(arch, '이미지 교체:', n)
    open(os.path.join(data_dir, 'sharedassets2.assets'), 'wb').write(env.file.save())


if __name__ == '__main__':
    # 미리보기: General Atlas만 렌더링해 저장
    env = UnityPy.load(os.path.join(GAME, '_original_backup', 'x64', 'FF9_Data', 'sharedassets2.assets'))
    for o in env.objects:
        if o.type.name == 'Texture2D' and o.peek_name() == 'General Atlas':
            img = o.read().image.convert('RGBA')
            for name, t, st, al, kl in GENERAL:
                r = sprite('sharedassets2.assets:General Atlas', name)
                put(img, r, render(t, r[2] - kl, r[3], st, al), kl)
            for name, t in HEADERS:
                header(img, sprite('sharedassets2.assets:General Atlas', name), t)
            bg = Image.new('RGBA', img.size, (40, 40, 90, 255)); bg.alpha_composite(img)
            bg.convert('RGB').save(os.path.join(W, 'tex', 'preview_general.jpg'))
