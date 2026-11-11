import json, pathlib, asyncio, html, sys, subprocess, shutil, os, re, hashlib
from playwright.async_api import async_playwright
R = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path('/home/claude/diwan.bizz/reels')
AUDIO = R/'nasheed.mp3'; AUDIO_LEN = 300
FPS = 24
AR = lambda n: str(n).translate(str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩'))
FD = R/'fonts'
F1 = (FD/'fontsource-reem-kufi-5.0.8/package/files/reem-kufi-arabic-700-normal.woff2').as_uri()
F2 = (FD/'fontsource-almarai-5.0.8/package/files/almarai-arabic-700-normal.woff2').as_uri()
F3 = (FD/'fontsource-almarai-5.0.8/package/files/almarai-arabic-800-normal.woff2').as_uri()
GD, LT, TX = '#A8894A', '#D9C79C', '#DADCCF'
THEME = {'قبل لا تفتح':'#2E3B24','معلومة إدارية':'#1E2A38','معلومة مالية':'#173832','تسويق ومبيعات':'#3A2024'}
def mark(w, anim=False):
    a = lambda d: f' style="transform-origin:center 90px;animation:grow .4s {d}s cubic-bezier(.2,.8,.2,1) both"' if anim else ''
    return (f'<svg viewBox="0 0 180 120" width="{w}"><rect x="10" y="40" width="44" height="50" rx="22" fill="{GD}"{a(.05)}/>'
            f'<rect x="68" y="24" width="44" height="66" rx="22" fill="{GD}"{a(.12)}/><rect x="126" y="10" width="44" height="80" rx="22" fill="{GD}"{a(.2)}/>'
            f'<rect x="0" y="98" width="180" height="16" rx="8" fill="{GD}"/></svg>')
LOCK = lambda anim=False: f'<div class="lock">{mark(150, anim)}<span>ديوان البزنس</span></div>'
def css(bg): return f'''@font-face{{font-family:K;src:url({F1})}}@font-face{{font-family:B;src:url({F2})}}@font-face{{font-family:H;src:url({F3})}}
*{{animation-play-state:paused!important}}
html,body{{margin:0;width:1080px;height:1920px;background:{bg};direction:rtl;overflow:hidden}}
.s{{box-sizing:border-box;width:1080px;height:1920px;padding:150px 100px 200px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;text-align:center;position:relative}}
.s:after{{content:"";position:absolute;inset:40px;border:2px solid rgba(168,137,74,.35);border-radius:32px}}
.lock{{display:flex;flex-direction:column;align-items:center;gap:22px;font-family:K;font-size:62px;color:{GD}}}
.chip{{font-family:H;font-size:50px;color:{bg};background:{GD};border-radius:16px;padding:14px 48px}}
h1{{font-family:H;font-size:104px;line-height:1.5;color:{LT};margin:0}}
h2{{font-family:H;font-size:84px;line-height:1.5;color:{LT};margin:0}}
p{{font-family:B;font-size:50px;line-height:1.75;color:{TX};margin:0}}
.num{{font-family:H;font-size:220px;line-height:1;color:{GD}}}
.mid{{display:flex;flex-direction:column;align-items:center;gap:44px}}
.bar{{height:6px;width:320px;background:{GD};border-radius:3px;transform-origin:center}}
.pg{{font-family:B;font-size:36px;color:{GD}}}
.up{{animation:up .4s cubic-bezier(.2,.8,.2,1) both}}
.pop{{animation:pop .4s cubic-bezier(.2,1.4,.4,1) both}}
.wide{{animation:wide .5s cubic-bezier(.2,.8,.2,1) both}}
.zoom{{animation:zoom .6s ease-out both}}
@keyframes up{{from{{opacity:0;transform:translateY(60px)}}to{{opacity:1;transform:none}}}}
@keyframes pop{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:none}}}}
@keyframes wide{{from{{transform:scaleX(0)}}to{{transform:none}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:none}}}}
@keyframes zoom{{from{{transform:scale(1)}}to{{transform:scale(1.04)}}}}'''
D = lambda d: f' style="animation-delay:{d}s"'
def page(p, i, s, n):
    series = p.get('series') or ''
    if s['k']=='cover':
        b = (f'{LOCK(False)}<div class="mid"><span class="chip">{html.escape(series)}</span>'
             f'<h1 class="zoom">{html.escape(s["h"])}</h1><div class="bar"></div></div><div class="pg">{AR(n-2)} نقاط · كمّل للآخر</div>')
    elif s['k']=='cta':
        b = (f'<div></div><div class="mid">{mark(300, True)}<span class="up" style="font-family:K;font-size:90px;color:{GD};animation-delay:.2s">ديوان البزنس</span>'
             f'<h2 class="up" style="font-size:64px;animation-delay:.3s">احفظ البوست وشاركه مع صاحب مشروع</h2><p class="up"{D(.4)}>وأنت؟ شاركنا رأيك أو تجربتك بالتعليقات 👇</p></div><div class="pg up"{D(.5)}>diwan.bizz</div>')
    else:
        b = (f'{LOCK()}<div class="mid"><div class="num pop">{AR(i)}</div><h2 class="up"{D(.06)}>{html.escape(s["h"])}</h2>'
             f'<div class="bar wide"{D(.12)}></div><p class="up"{D(.18)}>{html.escape(s["t"])}</p></div><div class="pg">{AR(i)} / {AR(n-2)}</div>')
    return f'<html><head><meta charset="utf-8"><style>{css(THEME.get(series,"#2E3B24"))}</style></head><body><div class="s">{b}</div></body></html>'
def slides(p):
    sl = p['slides']; pts = [x for x in sl[1:] if x.get('t') and x.get('h')!='احفظ البوست وارجع له قبل قرارك'][:5]
    return [dict(k='cover',h=sl[0]['h'])]+[dict(k='pt',h=x['h'],t=x['t']) for x in pts]+[dict(k='cta')]
def durs(sl):
    d=[2.0 if s['k']=='cover' else 2.8 if s['k']=='cta' else max(4.5, round(1.8+len(s['t'].split())*0.30,1)) for s in sl]
    pt=sum(x for x,s in zip(d,sl) if s['k']=='pt'); room=54.5-4.8
    if pt>room:
        f=room/pt; d=[x if s['k']!='pt' else max(4.0,round(x*f,1)) for x,s in zip(d,sl)]
    return d
async def build(pg, p):
    fr = R/'frames'/p['id']; shutil.rmtree(fr, ignore_errors=True); fr.mkdir(parents=True)
    tmp = R/f"vtmp_{p['id']}.html"; k = 0; sl = slides(p); n = len(sl); ds = durs(sl)
    for i,(s,d) in enumerate(zip(sl,ds)):
        tmp.write_text(page(p,i,s,n), encoding='utf-8')
        await pg.goto(tmp.as_uri()); await pg.evaluate('document.fonts.ready')
        end = await pg.evaluate('Math.max(0,...document.getAnimations().map(a=>{const t=a.effect.getComputedTiming();return t.delay+t.activeDuration}))')
        last=None
        for f in range(int(d*FPS)):
            t=f/FPS*1000
            if last and t>end+50: os.link(last, fr/f'{k:05d}.jpg'); k+=1; continue
            await pg.evaluate(f'document.getAnimations().forEach(a=>a.currentTime={t})')
            last=fr/f'{k:05d}.jpg'; await pg.screenshot(path=str(last), type='jpeg', quality=90); k+=1
    T=k/FPS; off=int(hashlib.md5(p['id'].encode()).hexdigest(),16)%max(1,int(AUDIO_LEN-T-5))+2
    out=OUT/f'{p["id"]}.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',str(fr/'%05d.jpg'),
        '-f','lavfi','-i','color=c=0xA8894A:s=1080x14:r=24',
        '-ss',str(off),'-i',str(AUDIO),
        '-filter_complex',f"[0:v][1:v]overlay=x='W-W*t/{T:.3f}':y=0:shortest=1[v]",
        '-map','[v]','-map','2:a','-t',f'{T:.2f}',
        '-af',f'volume=0.9,afade=t=in:st=0:d=0.4,afade=t=out:st={T-1.2:.2f}:d=1.2',
        '-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p','-crf','21','-movflags','+faststart','-c:a','aac','-b:a','160k',str(out)],check=True)
    shutil.copy(fr/'00000.jpg', OUT/f'{p["id"]}-cover.jpg'); shutil.rmtree(fr); tmp.unlink()
    return out, round(T,1)
async def main(ids):
    P={}
    for f in ids:
        p=json.load(open(f)); P[p['id']]=p
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1080,'height':1920})
        for pid,p in P.items(): print(*await build(pg,p), flush=True)
        await b.close()
asyncio.run(main(sys.argv[1:]))
