"""원본 TBUDGoStd-Bold에 한글 글리프 병합: python mergefont.py <한글폰트> <DY>"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
src, DY = sys.argv[1], int(sys.argv[2]); PAD = 6
a = TTFont('font/TBUDGoStd-Bold.otf'); n = TTFont(src)
ng = n.getGlyphSet(); ncm = n.getBestCmap()
glyf = a['glyf']; hmtx = a['hmtx']; order = a.getGlyphOrder()[:]
cps = list(range(0xAC00, 0xD7A4)) + list(range(0x3131, 0x318F)) + list(range(0x1100, 0x1200))
added = {}
for cp in cps:
    gn = ncm.get(cp)
    if gn is None: continue
    if gn not in added:
        name = 'kr%04X' % cp
        pen = TTGlyphPen(None)
        ng[gn].draw(TransformPen(pen, (1, 0, 0, 1, PAD, DY)))
        g = pen.glyph(); glyf[name] = g; order.append(name); g.recalcBounds(glyf)
        hmtx[name] = (ng[gn].width + 2 * PAD, getattr(g, 'xMin', 0))
        added[gn] = name
    for t in a['cmap'].tables:
        if t.isUnicode(): t.cmap[cp] = added[gn]
a.setGlyphOrder(order); glyf.glyphOrder = order; a['maxp'].numGlyphs = len(order)
a['post'].formatType = 3.0
a.save('font/merged.ttf'); print('glyphs', len(order))
