#!/usr/bin/env python3
"""메트로놈 가이드(41편) 번역판 생성기.

한국어 원문 페이지를 틀로 쓰고, i18n-src/guides/<lang>/*.txt 의 번역문으로
/<lang>/<slug> 페이지를 만든다. 한국어 원문에도 hreflang·언어 메뉴를 넣고 sitemap을 갱신한다.

번역 파일 형식 (한 파일에 여러 편 가능):
    ##### bpm-metronome          (폴더형은 bpm/ 처럼 끝에 /)
    TITLE: ...
    DESC: ...
    CRUMB: ...
    ---
    본문 HTML  ({{BRAND}} = 브랜드 문단+시작 버튼, {{LIST: /a /b}} = 허브 목록)

실행: python3 i18n-src/guides.py
"""
import html, json, pathlib, re, datetime, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "i18n-src" / "guides"
SITE = "https://tempo.dailydrum.co.kr"
APPSTORE = "https://apps.apple.com/app/id6808595998"

UI = {
    "en": dict(
        lang="en", locale="en_US", name="English", skip="Skip to content", home="TEMPO home",
        nav=["Features", "Guide", "Download"], guide="Metronome guide", story_aria="Why DailyDrum TEMPO",
        brand='TEMPO is a metronome app made by <strong>DailyDrum</strong>, a drum studio in Anyang (Pyeongchon), South Korea, where every lesson, from children to adults and church musicians, is taught one-on-one.',
        start="Start TEMPO free ↗",
        cta_h2='Starting with today’s practice, <em>at your tempo.</em>',
        cta_p="TEMPO, the metronome made by DailyDrum drum studio. Free to start. iPhone · iPad · Android",
        cta_btn="View on App Store ↗", more="More metronome guides", all="See all guides →",
        privacy="Privacy Policy", contact="Contact", lang_label="Language", all_langs="All languages (32)",
    ),
    "ja": dict(
        lang="ja", locale="ja_JP", name="日本語", skip="本文へスキップ", home="TEMPO ホーム",
        nav=["機能", "ガイド", "ダウンロード"], guide="メトロノームガイド", story_aria="なぜ DailyDrum の TEMPO なのか",
        brand='TEMPOは、韓国・安養（平村）で子どもから大人、教会の奏楽者まですべてのレッスンを1対1で行うドラム教室<strong>DailyDrum（デイリードラム）</strong>が作ったメトロノームアプリです。',
        start="TEMPOを無料ではじめる ↗",
        cta_h2='今日の練習から、<em>自分のテンポで。</em>',
        cta_p="ドラム教室 DailyDrum が作ったメトロノーム TEMPO。無料ではじめられます。iPhone · iPad · Android",
        cta_btn="App Storeで見る ↗", more="ほかのメトロノームガイド", all="すべてのガイドを見る →",
        privacy="プライバシーポリシー", contact="お問い合わせ", lang_label="言語", all_langs="すべての言語（32）",
    ),
}
import sys
sys.path.insert(0, str(ROOT / "i18n-src"))
import build as _home
GLOBE = re.search(r"<svg.*?</svg>", _home.switcher("ko", "x")).group(0)
LANGS = [c for c in UI if (SRC / c).is_dir()]


def ko_pages():
    pages = {}
    for f in sorted(ROOT.glob("*/index.html")) + sorted(ROOT.glob("*-*.html")):
        s = f.read_text(encoding="utf-8")
        if 'class="wrap article"' not in s:
            continue
        rel = f.relative_to(ROOT).as_posix()
        slug = rel.replace("/index.html", "/").replace(".html", "")
        s = re.sub(r"\n?<!--i18n-head-->.*?<!--/i18n-head-->", "", s, flags=re.S)
        s = re.sub(r"<!--i18n-sw-->.*?<!--/i18n-sw-->", "", s, flags=re.S)
        pages[slug] = (f, s)
    return pages


def parse_translations(code):
    out = {}
    for f in sorted((SRC / code).glob("*.txt")):
        for chunk in re.split(r"^##### ", f.read_text(encoding="utf-8"), flags=re.M)[1:]:
            key, rest = chunk.split("\n", 1)
            head, body = rest.split("\n---\n", 1)
            meta = dict(re.findall(r"^(TITLE|DESC|CRUMB): (.*)$", head, re.M))
            out[key.strip()] = dict(title=meta["TITLE"], desc=meta["DESC"], crumb=meta["CRUMB"], body=body.strip())
    return out


def url(code, slug):
    return f"{SITE}/{slug}" if code == "ko" else f"{SITE}/{code}/{slug}"


def alternates(slug, avail):
    links = [f'<link rel="alternate" hreflang="ko" href="{url("ko", slug)}">']
    links += [f'<link rel="alternate" hreflang="{UI[c]["lang"]}" href="{url(c, slug)}">' for c in avail]
    if "en" in avail:
        links.append(f'<link rel="alternate" hreflang="x-default" href="{url("en", slug)}">')
    return "\n".join(links)


def switcher(cur, slug, avail, label):
    names = {"ko": "한국어", **{c: UI[c]["name"] for c in avail}}
    items = "".join(
        f'<a href="/{"" if c == "ko" else c + "/"}{slug}" lang="{ "ko" if c == "ko" else UI[c]["lang"]}"'
        + (' aria-current="page"' if c == cur else "") + f">{n}</a>"
        for c, n in names.items()
    )
    items += f'<a href="{"/" if cur == "ko" else "/" + cur + "/"}" class="lang-more">{"전체 언어 (32)" if cur == "ko" else UI[cur]["all_langs"]}</a>'
    return (
        f'<details class="lang"><summary aria-label="{html.escape(label)}">{GLOBE}<span>{names[cur]}</span></summary>'
        f'<div class="lang-menu">{items}</div></details>'
        "<script>(function(){var d=document.currentScript.previousElementSibling;"
        "document.addEventListener('click',function(e){if(d.open&&!d.contains(e.target))d.open=false});"
        "document.addEventListener('keydown',function(e){if(e.key==='Escape')d.open=false})})();</script>"
    )


def rewrite_links(body, code, slugs):
    def fix(m):
        href = m.group(1)
        path = href.lstrip("/")
        if href == "/" or href.startswith("/#"):
            return f'href="/{code}{href}"'
        if path in slugs:
            return f'href="/{code}/{path}"'
        return m.group(0)
    return re.sub(r'href="(/[^"]*)"', fix, body)


def build_list(spec, code, tr):
    items = []
    for s in spec.split():
        p = tr[s.lstrip("/")]
        items.append(
            f'<li><a href="/{code}/{s.lstrip("/")}"><strong>{html.escape(p["crumb"])}</strong><br>'
            f'<span style="color:var(--muted);font-size:15px">{html.escape(p["desc"])}</span></a></li>'
        )
    return "<ul>" + "".join(items) + "</ul>"


def render(code, slug, ko_src, t, tr, slugs, avail):
    u = UI[code]
    s = ko_src
    title, desc = html.escape(t["title"]), html.escape(t["desc"])
    body = t["body"]
    body = body.replace("{{BRAND}}", f'<p class="brand-line">{u["brand"]}</p><a class="button primary" href="{APPSTORE}" target="_blank" rel="noopener">{u["start"]}</a>')
    body = body.replace('<section class="story">', f'<section class="story" aria-label="{html.escape(u["story_aria"])}">')
    body = re.sub(r"\{\{LIST:([^}]*)\}\}", lambda m: build_list(m.group(1), code, tr), body)
    body = rewrite_links(body, code, slugs)

    s = s.replace('<html lang="ko">', f'<html lang="{u["lang"]}">', 1)
    s = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", s, 1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, 1)
    s = re.sub(r'<meta name="keywords" content="[^"]*">\n?', "", s, 1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url(code, slug)}">\n{alternates(slug, avail)}', s, 1)
    s = s.replace('content="TEMPO - 데일리 드럼"', 'content="TEMPO - DailyDrum"')
    s = re.sub(r'(<meta property="og:url" content=")[^"]*', rf"\g<1>{url(code, slug)}", s, 1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, s, 1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, s, 1)
    s = s.replace('content="ko_KR"', f'content="{u["locale"]}"')
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": t["title"], "description": t["desc"],
          "inLanguage": u["lang"], "mainEntityOfPage": url(code, slug),
          "author": {"@type": "Organization", "name": "DailyDrum"},
          "publisher": {"@type": "Organization", "name": "DailyDrum", "logo": {"@type": "ImageObject", "url": f"{SITE}/tempo.png"}}}
    s = re.sub(r'<script type="application/ld\+json">.*?</script>',
               lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", s, 1, flags=re.S)
    s = s.replace('<link rel="stylesheet" href="/tempo-2026.css">', '<link rel="stylesheet" href="/tempo-2026.css"><link rel="stylesheet" href="/i18n.css">', 1)
    s = s.replace("본문으로 바로가기", u["skip"], 1)
    header = (f'<header class="wrap masthead"><a class="brand" href="/{code}/" aria-label="{u["home"]}"><img src="/brand.svg" alt="" width="38" height="38">'
              f'<span>TEMPO<small>DAILYDRUM</small></span></a><nav aria-label="Menu"><a href="/{code}/#features">{u["nav"][0]}</a>'
              f'<a href="/{code}/metronome/">{u["nav"][1]}</a><a href="/{code}/#download">{u["nav"][2]}</a>'
              f'{switcher(code, slug, avail, u["lang_label"])}</nav></header>')
    s = re.sub(r"<header .*?</header>", lambda m: header, s, 1, flags=re.S)
    crumbs = f'<p class="crumbs"><a href="/{code}/">TEMPO</a> › ' + (
        html.escape(u["guide"]) if slug == "metronome/" else f'<a href="/{code}/metronome/">{html.escape(u["guide"])}</a> › {html.escape(t["crumb"])}') + "</p>"
    cta = (f'<section class="cta"><div><h2>{u["cta_h2"]}</h2><p>{u["cta_p"]}</p></div>'
           f'<a class="button primary" href="{APPSTORE}" target="_blank" rel="noopener">{u["cta_btn"]}</a></section>')
    more = ""
    m = re.search(r'<nav class="more" aria-label="[^"]*">.*?</nav>', s, re.S)
    if m:
        li = "".join(f'<li><a href="/{code}/{x.lstrip("/")}">{html.escape(tr[x.lstrip("/")]["crumb"])} →</a></li>'
                     for x in re.findall(r'<li><a href="([^"]+)">', m.group(0)) if x.lstrip("/") in tr)
        more = (f'<nav class="more" aria-label="{html.escape(u["more"])}"><h2>{html.escape(u["more"])}</h2><ul>{li}</ul>'
                f'<p style="margin-top:14px"><a class="text-link" href="/{code}/metronome/">{html.escape(u["all"])}</a></p></nav>')
    article = f'<article class="wrap article">\n{crumbs}\n{body}\n{cta}\n{more}\n</article>'
    s = re.sub(r'<article class="wrap article">.*?</article>', lambda m: article, s, 1, flags=re.S)
    footer = (f'<footer class="wrap"><a class="brand" href="/{code}/">TEMPO<small>BY DAILYDRUM</small></a><div>'
              f'<a href="/{code}/metronome/">{u["guide"]}</a><a href="/privacy.html">{u["privacy"]}</a>'
              f'<a href="mailto:gksrlffh@naver.com">{u["contact"]}</a><a href="https://www.instagram.com/daily_drum_/" target="_blank" rel="noopener">Instagram ↗</a></div><p>© 2026 DailyDrum</p></footer>')
    s = re.sub(r"<footer .*?</footer>", lambda m: footer, s, 1, flags=re.S)
    return s


def patch_korean(slug, f, s, avail):
    s = re.sub(r"\n?<!--i18n-head-->.*?<!--/i18n-head-->", "", s, flags=re.S)
    s = re.sub(r"<!--i18n-sw-->.*?<!--/i18n-sw-->", "", s, flags=re.S)
    head = f'\n<!--i18n-head-->\n{alternates(slug, avail)}\n<link rel="stylesheet" href="/i18n.css">\n<!--/i18n-head-->'
    s = re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + head, s, 1)
    s = s.replace('<a href="/#download">다운로드</a></nav>',
                  '<a href="/#download">다운로드</a><!--i18n-sw-->' + switcher("ko", slug, avail, "언어 선택") + "<!--/i18n-sw--></nav>", 1)
    f.write_text(s, encoding="utf-8")


def patch_sitemap(done):
    p = ROOT / "sitemap.xml"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!--i18n-guides-->.*?<!--/i18n-guides-->\n?", "", s, flags=re.S)
    today = datetime.date.today().isoformat()
    rows = "".join(f"<url><loc>{url(c, sl)}</loc><lastmod>{today}</lastmod></url>\n" for c, sl in done)
    s = s.replace("</urlset>", f"<!--i18n-guides-->\n{rows}<!--/i18n-guides-->\n</urlset>")
    p.write_text(s, encoding="utf-8")


def main():
    pages = ko_pages()
    slugs = set(pages)
    trs = {c: parse_translations(c) for c in LANGS}
    done = []
    for slug, (f, src) in pages.items():
        avail = [c for c in LANGS if slug in trs[c]]
        for c in avail:
            missing = [x for x in slugs if x not in trs[c]]
            out = ROOT / c / (slug + "index.html" if slug.endswith("/") else slug + ".html")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render(c, slug, src, trs[c][slug], trs[c], set(trs[c]), avail), encoding="utf-8")
            done.append((c, slug))
        if avail:
            patch_korean(slug, f, src, avail)
    patch_sitemap(done)
    for c in LANGS:
        left = sorted(slugs - set(trs[c]))
        print(f"{c}: {len(trs[c])}편 생성" + (f", 남음 {len(left)}: {' '.join(left)}" if left else ""))


if __name__ == "__main__":
    main()
