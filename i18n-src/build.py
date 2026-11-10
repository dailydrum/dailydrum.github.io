#!/usr/bin/env python3
"""TEMPO 홈 다국어 페이지 생성기.

i18n-src/langs/<code>.json  →  /<code>/index.html
또 한국어 루트(index.html)에 언어 전환 메뉴·hreflang을 넣고 sitemap.xml을 갱신한다.
실행: python3 i18n-src/build.py
"""
import html, json, pathlib, re, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "i18n-src" / "langs"
SITE = "https://tempo.dailydrum.co.kr"
APPSTORE = "https://apps.apple.com/app/id6808595998"
PLAY = "https://play.google.com/store/apps/details?id=com.dailydrum.metronome"

# (경로, html lang, 메뉴 표시 이름, og:locale, rtl)
LANGS = [
    ("ko", "ko", "한국어", "ko_KR", False),
    ("en", "en", "English", "en_US", False),
    ("ja", "ja", "日本語", "ja_JP", False),
    ("zh-hans", "zh-Hans", "简体中文", "zh_CN", False),
    ("zh-hant", "zh-Hant", "繁體中文", "zh_TW", False),
    ("es", "es", "Español", "es_ES", False),
    ("pt", "pt", "Português", "pt_BR", False),
    ("de", "de", "Deutsch", "de_DE", False),
    ("fr", "fr", "Français", "fr_FR", False),
    ("it", "it", "Italiano", "it_IT", False),
    ("nl", "nl", "Nederlands", "nl_NL", False),
    ("ru", "ru", "Русский", "ru_RU", False),
    ("uk", "uk", "Українська", "uk_UA", False),
    ("pl", "pl", "Polski", "pl_PL", False),
    ("cs", "cs", "Čeština", "cs_CZ", False),
    ("hu", "hu", "Magyar", "hu_HU", False),
    ("ro", "ro", "Română", "ro_RO", False),
    ("el", "el", "Ελληνικά", "el_GR", False),
    ("tr", "tr", "Türkçe", "tr_TR", False),
    ("ar", "ar", "العربية", "ar_AR", True),
    ("he", "he", "עברית", "he_IL", True),
    ("hi", "hi", "हिन्दी", "hi_IN", False),
    ("bn", "bn", "বাংলা", "bn_BD", False),
    ("id", "id", "Bahasa Indonesia", "id_ID", False),
    ("ms", "ms", "Bahasa Melayu", "ms_MY", False),
    ("vi", "vi", "Tiếng Việt", "vi_VN", False),
    ("th", "th", "ไทย", "th_TH", False),
    ("fil", "fil", "Filipino", "tl_PH", False),
    ("sv", "sv", "Svenska", "sv_SE", False),
    ("nb", "nb", "Norsk", "nb_NO", False),
    ("da", "da", "Dansk", "da_DK", False),
    ("fi", "fi", "Suomi", "fi_FI", False),
]


# 번역 파일이 있는 언어만 사용
LANGS = [l for l in LANGS if l[0] == "ko" or (SRC / f"{l[0]}.json").exists()]


def url(code):
    return f"{SITE}/" if code == "ko" else f"{SITE}/{code}/"


def path(code):
    return "/" if code == "ko" else f"/{code}/"


def hreflang_links():
    out = [f'<link rel="alternate" hreflang="{lang}" href="{url(code)}">' for code, lang, *_ in LANGS]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{url("en")}">')
    return "\n".join(out)


def switcher(current, label):
    name = next(n for c, _, n, *_ in LANGS if c == current)
    items = "".join(
        f'<a href="{path(c)}" hreflang="{l}" lang="{l}"'
        + (' aria-current="page"' if c == current else "")
        + f">{n}</a>"
        for c, l, n, *_ in LANGS
    )
    return (
        f'<details class="lang"><summary aria-label="{html.escape(label)}">'
        f'<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.9 6h-2.9a15.6 15.6 0 0 0-1.4-3.6A8 8 0 0 1 18.9 8ZM12 4c.8 1.2 1.5 2.5 1.9 4h-3.8c.4-1.5 1.1-2.8 1.9-4ZM4.3 14a8.2 8.2 0 0 1 0-4h3.4a16.5 16.5 0 0 0 0 4H4.3Zm.8 2h2.9c.3 1.3.8 2.5 1.4 3.6A8 8 0 0 1 5.1 16ZM8 8H5.1a8 8 0 0 1 4.3-3.6C8.8 5.5 8.3 6.7 8 8Zm4 12c-.8-1.2-1.5-2.5-1.9-4h3.8c-.4 1.5-1.1 2.8-1.9 4Zm2.3-6H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4Zm.3 5.6c.6-1.1 1.1-2.3 1.4-3.6h2.9a8 8 0 0 1-4.3 3.6Zm1.7-5.6a16.5 16.5 0 0 0 0-4h3.4a8.2 8.2 0 0 1 0 4h-3.4Z"/></svg>'
        f"<span>{name}</span></summary><div class=\"lang-menu\">{items}</div></details>"
        "<script>(function(){var d=document.currentScript.previousElementSibling;"
        "document.addEventListener('click',function(e){if(d.open&&!d.contains(e.target))d.open=false});"
        "document.addEventListener('keydown',function(e){if(e.key==='Escape')d.open=false})})();</script>"
    )


def br(s):
    return html.escape(s).replace("\n", "<br>")


def lis(items):
    return "".join(f"<li>{html.escape(i)}</li>" for i in items)


def render(code, lang, name, locale, rtl, t):
    e = lambda k: html.escape(t[k])
    b = lambda k: br(t[k])
    new = "".join(f"<li><strong>{html.escape(a)}</strong><span>{html.escape(d)}</span></li>" for a, d in t["new_items"])
    return f"""<!doctype html>
<html lang="{lang}"{' dir="rtl"' if rtl else ''}><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e('title')}</title>
<meta name="description" content="{e('desc')}">
<link rel="canonical" href="{url(code)}">
{hreflang_links()}
<meta property="og:type" content="website">
<meta property="og:site_name" content="TEMPO - DailyDrum">
<meta property="og:url" content="{url(code)}">
<meta property="og:title" content="{e('title')}">
<meta property="og:description" content="{e('desc')}">
<meta property="og:image" content="{SITE}/tempo.png">
<meta property="og:locale" content="{locale}">
<link rel="icon" href="/brand.svg"><link rel="stylesheet" href="/tempo-2026.css"><link rel="stylesheet" href="/i18n.css">
</head><body>
<a class="skip" href="#main">{e('skip')}</a>
<header class="wrap masthead"><a class="brand" href="#top" aria-label="TEMPO"><img src="/brand.svg" alt="" width="38" height="38"><span>TEMPO<small>DAILYDRUM</small></span></a><nav aria-label="Menu"><a href="#features">{e('nav_features')}</a><a href="#changes">{e('nav_new')}</a><a href="#download">{e('nav_download')}</a>{switcher(code, t['lang_label'])}</nav></header>
<main id="main">
<section class="wrap hero" id="top">
<div class="hero-copy"><p class="eyebrow">YOUR RHYTHM. EVERY DAY.</p><h1>{e('h1a')}<br><em>{e('h1b')}</em></h1><p class="lead">{b('lead')}</p><div class="actions"><a class="button primary" href="#download">{e('cta')}</a><a class="text-link" href="#features">{e('cta2')} ↓</a></div><p class="secondary">Metronome · List · Live · Playback</p></div>
<figure class="hero-image"><img src="/assets/2.5/01-tempo.png" alt="{e('hero_alt')}" width="1320" height="2868" fetchpriority="high"><figcaption>{e('hero_cap')}</figcaption></figure></section>
<aside class="release wrap" aria-label="{e('release_t')}"><strong>{e('release_t')}</strong><p>{e('release_p')}</p><a href="#changes">{e('nav_new')} ↓</a></aside>
<section class="wrap feature-intro" id="features"><p class="eyebrow">FROM PRACTICE TO STAGE</p><h2>{b('intro_h2')}</h2><p>{e('intro_p')}</p></section>
<section class="wrap feature spotlight"><div class="feature-copy"><p class="eyebrow">PLAYBACK</p><h2>{b('pb_h2')}</h2><p>{e('pb_p')}</p><ul>{lis(t['pb_li'])}</ul><p class="secondary">{e('pb_note')}</p></div><figure><img src="/assets/2.5/04-playback.png" alt="{e('pb_alt')}" width="1320" height="2868" loading="lazy"></figure></section>
<section class="wrap feature spotlight"><div class="feature-copy"><p class="eyebrow">MIXED METER</p><h2>{b('mm_h2')}</h2><p>{e('mm_p')}</p><p class="secondary">{e('mm_steps')}</p></div><figure><img src="/assets/2.5/05-mixed-meter.png" alt="{e('mm_alt')}" width="1320" height="2868" loading="lazy"></figure></section>
<section class="wrap feature spotlight"><div class="feature-copy"><p class="eyebrow">DRUM MACHINE</p><h2>{b('dm_h2')}</h2><p>{e('dm_p')}</p><ul>{lis(t['dm_li'])}</ul><p class="secondary">{e('dm_secret')}</p></div><figure><img src="/assets/2.5/08-drums.png" alt="{e('dm_alt')}" width="1320" height="2868" loading="lazy"></figure></section>
<section class="wrap feature-grid">
<article><div class="card-copy"><p class="eyebrow">LIST</p><h3>{b('list_h3')}</h3><p>{e('list_p')}</p><p class="secondary">{e('list_note')}</p></div><img src="/assets/2.5/02-list.png" alt="{e('list_alt')}" width="1320" height="2868" loading="lazy"></article>
<article><div class="card-copy"><p class="eyebrow">LIVE</p><h3>{b('live_h3')}</h3><p>{e('live_p')}</p><p class="secondary">{e('live_note')}</p></div><img src="/assets/2.5/03-live.png" alt="{e('live_alt')}" width="1320" height="2868" loading="lazy"></article>
<article><div class="card-copy"><p class="eyebrow">LIST · PRACTICE</p><h3>{b('pr_h3')}</h3><p>{e('pr_p')}</p><p class="secondary">{e('pr_note')}</p></div><img src="/assets/2.5/09-practice.png" alt="{e('pr_alt')}" width="1320" height="2868" loading="lazy"></article>
<article><div class="card-copy"><p class="eyebrow">VOICE &amp; SOUND</p><h3>{b('vs_h3')}</h3><p>{e('vs_p')}</p><p class="secondary">{e('vs_note')}</p></div><img src="/assets/2.5/07b-sound-options.png" alt="{e('vs_alt')}" width="1320" height="2868" loading="lazy"></article>
</section>
<section class="wrap updates" id="changes"><div><p class="eyebrow">WHAT'S NEW / 2.5.3</p><h2>{b('new_h2')}</h2></div><ul>{new}</ul></section>
<section class="wrap feature spotlight" id="pro"><div class="feature-copy"><p class="eyebrow">TEMPO PRO · iOS</p><h2>{b('pro_h2')}</h2><p>{e('pro_p')}</p><ul>{lis(t['pro_li'])}</ul><p class="secondary">{e('pro_note')}</p></div><div class="card-copy"><p class="eyebrow">START FREE</p><h3>{e('free_h3')}</h3><p>{e('free_p1')}</p><p>{e('free_p2')}</p></div></section>
<section class="download wrap" id="download"><div><p class="eyebrow">READY FOR YOUR NEXT BEAT?</p><h2>{e('dl_h2a')}<br><em>{e('dl_h2b')}</em></h2></div><div class="download-links"><a class="button primary" href="{APPSTORE}" target="_blank" rel="noopener">App Store ↗</a><p>iPhone · iPad</p><a class="button outline" href="{PLAY}" target="_blank" rel="noopener">Google Play ↗</a><p>Android</p></div></section>
</main><footer class="wrap"><a class="brand" href="#top">TEMPO<small>BY DAILYDRUM</small></a><div><a href="/privacy.html">{e('privacy')}</a><a href="mailto:gksrlffh@naver.com">{e('contact')}</a><a href="https://www.instagram.com/daily_drum_/" target="_blank" rel="noopener">Instagram ↗</a></div><p>© 2026 DailyDrum</p></footer>
</body></html>
"""


# 한국어 루트: 언어 메뉴·hreflang·외국어 안내 배너 삽입 (마커로 재실행해도 중복 없음)
SUGGEST_JS = """<script>/*i18n-suggest*/(function(){try{if(localStorage.getItem('tempoLangDismiss'))return}catch(e){}
var L=%s;var n=(navigator.languages||[navigator.language||'']).map(function(x){return (x||'').toLowerCase()});
if(!n.length||/^ko/.test(n[0]))return;var p=n[0],c=null;
if(/^zh/.test(p))c=/(tw|hk|mo|hant)/.test(p)?'zh-hant':'zh-hans';else if(/^(nb|nn|no)/.test(p))c='nb';else if(/^(tl|fil)/.test(p))c='fil';else if(/^(iw|he)/.test(p))c='he';else{var b=p.split('-')[0];if(L[b])c=b}
if(!c)c='en';var d=document.createElement('div');d.className='lang-suggest';d.setAttribute('lang',c);
d.innerHTML='<a href="/'+c+'/">'+L[c]+' →</a><button type="button" aria-label="Close">×</button>';
d.querySelector('button').onclick=function(){d.remove();try{localStorage.setItem('tempoLangDismiss','1')}catch(e){}};
document.body.insertBefore(d,document.body.firstChild)})();</script>"""


def patch_korean_root(hints):
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"\n?<!--i18n-head-->.*?<!--/i18n-head-->", "", s, flags=re.S)
    s = re.sub(r"<!--i18n-sw-->.*?<!--/i18n-sw-->", "", s, flags=re.S)
    s = re.sub(r"<!--i18n-js-->.*?<!--/i18n-js-->", "", s, flags=re.S)
    head = f"\n<!--i18n-head-->\n{hreflang_links()}\n<link rel=\"stylesheet\" href=\"./i18n.css\">\n<!--/i18n-head-->"
    s = s.replace('<link rel="icon" href="./brand.svg"><link rel="stylesheet" href="./tempo-2026.css">',
                  '<link rel="icon" href="./brand.svg"><link rel="stylesheet" href="./tempo-2026.css">' + head, 1)
    s = s.replace('<a href="#download">다운로드</a></nav>',
                  '<a href="#download">다운로드</a><!--i18n-sw-->' + switcher("ko", "언어 선택") + "<!--/i18n-sw--></nav>", 1)
    js = "<!--i18n-js-->" + SUGGEST_JS % json.dumps(hints, ensure_ascii=False) + "<!--/i18n-js-->"
    s = s.replace("</body></html>", js + "\n</body></html>", 1)
    p.write_text(s, encoding="utf-8")


def patch_sitemap():
    p = ROOT / "sitemap.xml"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!--i18n-->.*?<!--/i18n-->\n?", "", s, flags=re.S)
    today = datetime.date.today().isoformat()
    rows = "".join(f"<url><loc>{url(c)}</loc><lastmod>{today}</lastmod></url>\n" for c, *_ in LANGS if c != "ko")
    s = s.replace("</urlset>", f"<!--i18n-->\n{rows}<!--/i18n-->\n</urlset>")
    p.write_text(s, encoding="utf-8")


def main():
    hints = {}
    required = None
    for code, lang, name, locale, rtl in LANGS:
        if code == "ko":
            continue
        t = json.loads((SRC / f"{code}.json").read_text(encoding="utf-8"))
        if required is None:
            required = set(json.loads((SRC / "en.json").read_text(encoding="utf-8")))
        missing = required - set(t)
        if missing:
            raise SystemExit(f"{code}: 빠진 키 {sorted(missing)}")
        hints[code] = t["view_in"]
        out = ROOT / code / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(render(code, lang, name, locale, rtl, t), encoding="utf-8")
    patch_korean_root(hints)
    patch_sitemap()
    print(f"{len(hints)}개 언어 생성 완료")


if __name__ == "__main__":
    main()
