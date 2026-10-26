"""merged.ttf를 원본 폰트 번들에 넣어 font/p_fa_new.bundle 생성"""
import UnityPy, json
c = json.load(open('container.json')); pid = [p for k, f, p in c if k == 'embeddedasset/fa/p_fa.mpc'][0]
env = UnityPy.load('../_original_backup/x64/FF9_Data/resources.assets')
o = [o for o in env.objects if o.path_id == pid][0]; s = o.read().m_Script
b = s.encode('utf-8', 'surrogateescape') if isinstance(s, str) else bytes(s)
fb = UnityPy.load(b[-1024:] + b[1024:len(b) - 1024])
data = open('font/merged.ttf', 'rb').read()
for o in fb.objects:
    if o.type.name == 'Font':
        tt = o.read_typetree(); tt['m_FontData'] = list(data) if isinstance(tt['m_FontData'], list) else data; o.save_typetree(tt)
open('font/p_fa_new.bundle', 'wb').write(list(fb.files.values())[0].save()); print('bundle ok')
