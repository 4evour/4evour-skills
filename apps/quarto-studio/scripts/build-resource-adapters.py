from pathlib import Path
import json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
UP=ROOT/'resources/upstream/typst'
OUT=ROOT/'styles/resources/runtime'

def replace(text, old, new):
    if old not in text: raise ValueError('适配定位失败：'+old[:90])
    return text.replace(old,new)

def image_backgrounds(text):
    # 只替换页背景表达式；正文组件名为 background 的字段保持原样。
    start = 0
    while True:
        match = re.search(r"background: (place\()", text[start:])
        if not match:
            break
        opening = start + match.end() - 1
        depth, end = 1, opening + 1
        while depth:
            if text[end] == "(": depth += 1
            elif text[end] == ")": depth -= 1
            end += 1
        begin = start + match.start() + len("background: ")
        original = text[begin:end]
        replacement = 'if studio.at("image-path", default: none) != none { studio.texture } else { ' + original + ' }'
        text = text[:begin] + replacement + text[end:]
        start = begin + len(replacement)
    return text.replace('background: none', 'background: if studio.at("image-path", default: none) != none { studio.texture } else { none }')

def build():
    entries={}
    for package in UP.iterdir():
        for version in package.iterdir():
            info={"entrypoint": re.search(r'entrypoint\s*=\s*"([^"]+)"', (version/"typst.toml").read_text(encoding="utf-8"))[1]}
            entries[(package.name,version.name)]='/styles/resources/runtime/'+package.name+'/'+version.name+'/'+info['entrypoint']
    for package in UP.iterdir():
        for version in package.iterdir():
            for data in version.rglob('*'):
                if data.is_file() and (data.suffix in ('.yaml', '.yml', '.json', '.csv', '.png', '.jpg', '.svg') or data.name.upper().startswith(('LICENSE', 'LICENCE'))):
                    target=OUT/package.name/version.name/data.relative_to(version)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(data,target)
            for file in version.rglob('*.typ'):
                text=file.read_text(encoding='utf-8')
                text=re.sub(r'@preview/([\w-]+):([\d.]+)',lambda m:entries[(m[1],m[2])],text)
                text=text.replace('image("assets/','image("/resources/upstream/typst/'+package.name+'/'+version.name+'/assets/')
                is_entry=file.name==Path(entries[(package.name,version.name)]).name
                if is_entry:
                    n=package.name
                    if n=='dashing-dept-news':
                        text=replace(text,'  body\n) =','  studio: (:),\n  body\n) =')
                        text=text.replace('fill: red','fill: studio.accent').replace('rgb("FF7D79")','studio.panel')
                        text=text.replace('"Barlow"','studio.body-font').replace('"Syne Tactile"','studio.heading-font').replace('"Syne"','studio.heading-font')
                        text=text.replace('set text(12pt,','set text(studio.fontsize,')
                        text=text.replace('margin: (left: 2.5cm, right: 1.6cm),','width: studio.width, height: studio.height,\n    fill: studio.paper, margin: (x: studio.margin-x, y: studio.margin-y),')
                        text=text.replace('7.8cm','(studio.width * 0.32)').replace('1.6cm','studio.margin-x')
                        text=text.replace('23pt, weight: 800','studio.heading-size, weight: 800')
                        text=text.replace('set par(justify: true)','set par(justify: false, leading: studio.leading, spacing: studio.spacing)')
                    elif n=='wonderous-book':
                        text=replace(text,'  body,\n) =','  studio: (:),\n  body,\n) =')
                        text=text.replace('font: "TeX Gyre Pagella"','font: studio.body-font, size: studio.fontsize, fill: studio.ink, lang: "zh"')
                        text=text.replace('paper: paper-size,','width: studio.width, height: studio.height, fill: studio.paper,')
                        text=text.replace('margin: (bottom: 1.75cm, top: 2.25cm),','margin: (x: studio.margin-x, y: studio.margin-y),')
                        start=text.index('  // The first page.');end=text.index('  // Configure paragraph properties.')
                        text=text[:start]+'  if studio.cover {\n'+text[start:end]+'\n  }\n'+text[end:]
                        text=text.replace('pagebreak(to: to)', 'pagebreak(weak: true)')
                        text=text.replace('pagebreak(to: "odd")','pagebreak()').replace('pagebreak(to: "odd", weak: true)','pagebreak(weak: true)')
                        text=text.replace('outline(title: [Chapters])\n  pagebreak(weak: true)','if studio.toc { outline(title: [目录]); pagebreak(weak: true) }')
                        text=text.replace('set par(spacing: 0.78em, leading: 0.78em','set par(spacing: studio.spacing, leading: studio.leading')
                        text=text.replace('pagebreak()', 'pagebreak(weak: true)')
                    elif n=='orange-book':
                        text=replace(text,'#let book(title:','#let book(studio: (:), title:')
                        text=text.replace('set text(size: font-size, lang: lang)','set text(size: font-size, lang: lang, font: studio.body-font, fill: studio.ink)')
                        text=text.replace('font: "OPTIOriginal", fallback: false','font: "Source Han Serif SC", fallback: true')
                        a=text.index('  // Title page.');b=text.index('  heading-image.update',a)
                        text=text[:a]+'  if studio.cover {\n'+text[a:b]+'\n  }\n'+text[b:]
                        a=text.index('  my-outline(appendix-state');b=text.index('\n',a)
                        text=text[:a]+'  if studio.toc {\n'+text[a:b]+'\n  }'+text[b:]
                        text=text.replace('pagebreak(to: "odd")','pagebreak(weak: true)')
                    elif n=='vibrant-color':
                        text=replace(text,'  doc,\n) =>','  studio: (:),\n  doc,\n) =>')
                        text=text.replace('let theme-color = if theme ==','let theme-color = if studio.accent != none { studio.accent.to-hex() } else if theme ==')
                        text=text.replace('("Stretch Pro", "Arial", "Liberation Sans")','(studio.heading-font, "Source Han Sans SC")').replace('("Metropolis", "Arial", "Liberation Sans")','(studio.body-font, "Source Han Serif SC")')
                        text=text.replace('set page("a4", margin: 0cm)','set page(width: studio.width, height: studio.height, margin: 0cm, fill: studio.paper)')
                        text=text.replace('set text(lang: lang, font: normal-fonts)','set text(lang: "zh", font: normal-fonts, size: studio.fontsize, fill: studio.ink)')
                        first_bold = '  let first-bold = text => {\n    let words = text.split(" ")\n    upper(strong(words.first()) + " " + words.at(1))\n  }'
                        text=replace(text, first_bold, '')
                        text=text.replace('  // Metadata', first_bold.replace('words.at(1)', 'words.at(1, default: "")')+'\n\n  // Metadata')
                        a=text.index('  // Cover image');b=text.index('  /* -------------------------------------------\n  *  Table of contents')
                        text=text[:a]+'  if studio.cover {\n'+text[a:b]+'  }\n'+text[b:]
                        a=text.index('  pagebreak()',text.index('*  Table of contents'));b=text.index('  /* -------------------------------------------\n  *  Report body')
                        text=text[:a]+'  if studio.toc {\n'+text[a:b]+'  }\n'+text[b:]
                        text=text.replace('if lang == "fr" [SOMMAIRE] else [SUMMARY]','[目录]')
                        end_marker=text.index('*  End page')
                        a=text.index('  pagebreak()', end_marker)
                        b=text.index('\n}', a)
                        text=text[:a]+'  if studio.cover {\n'+text[a:b]+'\n  }'+text[b:]
                        a=text.index('  // Displays the side-bar (placed in the "footer" element)')
                        b=text.index('  /* -------------------------------------------', a)
                        text=text[:a]+'  set page(footer: if studio.footer { context align(right, text(size: 9pt, fill: studio.ink, counter(page).display("1"))) } else { none })\n\n'+text[b:]
                        text=text.replace('set page(margin: 0cm, background: none)', 'set page(margin: 0cm, background: none, header: none, footer: none)')
                        # 保留上游侧栏，页边距转为当前设置。
                        text=text.replace('top: 1cm,\n      bottom: 1cm,\n      left: 2.2cm,\n      right: 1.12cm,','top: studio.margin-y, bottom: studio.margin-y,\n      left: studio.margin-x + 16pt, right: studio.margin-x,')
                    elif n=='modern-technique-report':
                        text=replace(text,'  doc\n) =','  studio: (:),\n  doc\n) =')
                        text=text.replace('set text(font: font)','set text(font: font, size: studio.fontsize, fill: studio.ink, lang: "zh")')
                        a=text.index('  // Cover begin');b=text.index('  // Cover end')
                        text=text[:a]+'  if studio.cover {\n'+text[a:b]+'  }\n'+text[b:]
                        a=text.index('  show outline.entry.where(');b=text.index('  outline(',a)
                        text=text[:a]+'  show outline.entry.where(level: 1): set text(13pt, font: title-font, weight: "bold", fill: font-color)\n  set outline.entry(fill: repeat[.])\n'+text[b:]
                        text=text.replace('    depth: 2,\n    fill: repeat[#text(fill: gray)[.]]', '    title: [目录], depth: 2')
                        a=text.index('  // Outline begin');b=text.index('  // Outline end')
                        text=text[:a]+'  if studio.toc {\n'+text[a:b]+'  pagebreak()\n  }\n'+text[b:]
                    elif n=='ilm':
                        text=replace(text,'  body,\n) =','  studio: (:),\n  body,\n) =')
                        text=text.replace('set text(size: 12pt)','set text(font: studio.body-font, size: studio.fontsize, fill: studio.ink, lang: "zh")')
                        text=text.replace('paper: paper-size,','width: studio.width, height: studio.height, fill: studio.paper,')
                        text=text.replace('margin: (bottom: 1.75cm, top: 2.25cm),','margin: (x: studio.margin-x, y: studio.margin-y),')
                if is_entry and package.name in ('dashing-dept-news', 'vibrant-color'):
                    text = image_backgrounds(text)
                target=OUT/package.name/version.name/file.relative_to(version)
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text('// Quarto Studio 中文及控制台适配；原始源码、许可见 resources/upstream。\n'+text,encoding='utf-8')
    # Tufte 本身就是一个 Quarto 模板；转换其定义文件中的少量模板条件。
    tufte=ROOT/'resources/upstream/quarto/tufte/_extensions/tufte'
    defs=(tufte/'definitions.typ').read_text(encoding='utf-8')
    defs=re.sub(r'\$if\(sansfont\)\$.*?\$endif\$', '#let sansfont = "Source Han Sans SC"', defs, flags=re.S)
    defs=defs.replace('@preview/drafting:0.2.2',entries[('drafting','0.2.2')])
    body=(tufte/'typst-template.typ').read_text(encoding='utf-8')
    body=body.replace('  title: none,','  studio: (:),\n  title: none,',1)
    body=body.replace('paper: "us-letter",\n    margin: (\n      left: 1in,\n      right: 3.5in,\n      top: 1.5in,\n      bottom: 1.5in,\n    ),','width: studio.width, height: studio.height, fill: studio.paper,\n    margin: (left: studio.margin-x, right: studio.margin-x + 110pt, y: studio.margin-y),')
    body=body.replace('"Lucida Console"','studio.code-font').replace('fill: luma(30)','fill: studio.ink')
    body=body.replace('100% + 3.5in - 1in', '100% + 110pt')
    body=body.replace('margin-right: 2.35in', 'margin-right: 110pt')
    body=body.replace('show par: set block(spacing: 0.65em)', 'set par(spacing: 0.65em)')
    body=body.replace('margin-right: 2.35in','margin-right: 110pt').replace('margin-left: 1.35in','margin-left: studio.margin-x')
    body=body.replace('background: if draft {', 'background: if studio.at("image-path", default: none) != none { studio.texture } else if draft {')
    (OUT/'tufte.typ').write_text(defs+'\n'+body,encoding='utf-8')
    shutil.copyfile(ROOT/'resources/upstream/quarto/tufte/LICENSE', OUT/'tufte.LICENSE')

if __name__=='__main__':
    build()
    print('模板与组件适配已生成。')
