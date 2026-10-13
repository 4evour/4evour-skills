// 主题色和字体可由 YAML 覆盖；只使用本机已验证可用的字体。
#let design-theme = "$design-theme$"
#let palettes = (
  magazine: (paper: "#F6F2EA", ink: "#202B36", muted: "#6D747D", accent: "#B7472A", panel: "#ECE7DD", line: "#D8D0C2", dark: false),
  report: (paper: "#FFFFFF", ink: "#193040", muted: "#607786", accent: "#087F86", panel: "#EDF5F5", line: "#D5E5E7", dark: false),
  night: (paper: "#182329", ink: "#F3F0E8", muted: "#A7BCBF", accent: "#F2C875", panel: "#24353D", line: "#435A63", dark: true),
)
#let palette = palettes.at(design-theme, default: palettes.magazine)
#let paper = $if(design-paper)$rgb(content-to-string([$design-paper$]))$else$rgb(palette.paper)$endif$
#let ink = $if(design-ink)$rgb(content-to-string([$design-ink$]))$else$rgb(palette.ink)$endif$
#let muted = $if(design-muted)$rgb(content-to-string([$design-muted$]))$else$rgb(palette.muted)$endif$
#let accent = $if(design-accent)$rgb(content-to-string([$design-accent$]))$else$rgb(palette.accent)$endif$
#let panel = $if(design-panel)$rgb(content-to-string([$design-panel$]))$else$rgb(palette.panel)$endif$
#let divider = rgb(palette.line)
#let heading-font = $if(design-heading-font)$"$design-heading-font$"$else$"Microsoft YaHei"$endif$
#let body-font = $if(design-body-font)$"$design-body-font$"$else$"Noto Sans SC"$endif$
#let quote-font = $if(design-quote-font)$"$design-quote-font$"$else$"KaiTi"$endif$

#let background-pattern = "$design-background-pattern$"
#let page-texture = {
  if background-pattern == "grid" {
    for x in range(0, 26) { place(top + left, dx: x * 24pt, line(start: (0pt, 0pt), end: (0pt, 792pt), stroke: 0.35pt + divider)) }
    for y in range(0, 34) { place(top + left, dy: y * 24pt, line(length: 612pt, stroke: 0.35pt + divider)) }
  } else if background-pattern == "dots" {
    for x in range(0, 26) { for y in range(0, 34) { place(top + left, dx: x * 24pt, dy: y * 24pt, circle(radius: 0.6pt, fill: divider)) } }
  }
}
// 可复用内容组件：标签、提示卡片、双栏信息、金句、时间线。
#let tag(body) = box(fill: accent, radius: 4pt, inset: (x: 9pt, y: 5pt))[
  #text(font: heading-font, size: 10pt, weight: "bold", fill: paper)[#body]
]
#let note-card(title: "重点", body) = block(
  width: 100%, fill: panel, radius: 9pt, inset: 18pt,
  stroke: (left: 3pt + accent, rest: none), above: 14pt, below: 14pt,
  breakable: false,
)[
  #text(font: heading-font, size: 14pt, weight: "bold", fill: accent)[#title]
  #v(7pt)
  #text(size: 13.5pt)[#body]
]
#let feature-card(number: "01", title: "标题", body) = block(
  width: 100%, height: 118pt, fill: panel, radius: 9pt, inset: 16pt,
  breakable: false,
)[
  #text(font: "Georgia", size: 25pt, fill: accent)[#number]
  #v(5pt)
  #text(font: heading-font, size: 14pt, weight: "bold")[#title]
  #v(6pt)
  #text(size: 11.5pt, fill: muted)[#body]
]
#let pull-quote(body, by: none) = block(
  width: 100%, inset: (x: 21pt, y: 18pt), above: 16pt, below: 16pt,
  stroke: (left: 2pt + accent, rest: none), breakable: false,
)[
  #text(font: quote-font, size: 23pt, fill: accent)[#body]
  #if by != none [#v(9pt) #text(font: body-font, size: 11pt, fill: muted)[#by]]
]
#let step(number, title, body) = grid(
  columns: (33pt, 1fr), column-gutter: 13pt,
  align: (left, left),
  circle(radius: 15pt, fill: accent)[#align(center + horizon, text(size: 11pt, weight: "bold", fill: paper, number))],
  block(below: 18pt)[
    #text(font: heading-font, size: 14pt, weight: "bold")[#title]
    #v(5pt)
    #text(size: 12pt, fill: muted)[#body]
  ],
)

#let designed-article(title: none, subtitle: none, author: none, date: none,
  toc: false, toc-title: "目录", toc-depth: 2, fontsize: 16.5pt, doc) = {
  set document(title: title)
  if author != none { set document(author: content-to-string(author)) }
  set text(font: (body-font, "Microsoft YaHei"), size: fontsize, fill: ink, lang: "zh", region: "CN")
  set par(leading: $if(design-leading)$$design-leading$em$else$0.64em$endif$, spacing: 0.95em, justify: false)
  set page(fill: paper, background: page-texture, numbering: none, header: none, footer: none)
  set heading(numbering: none)
  show heading: set text(font: heading-font, weight: "bold", fill: ink)
  show heading.where(level: 1): it => block(above: 0pt, below: 19pt)[
    #text(font: "Georgia", size: 10pt, fill: accent, tracking: 1.5pt)[ARTICLE / DESIGN NOTES]
    #v(8pt)
    #text(font: heading-font, size: $if(design-heading-size)$$design-heading-size$pt$else$28pt$endif$, weight: "bold")[#it.body]
    #v(10pt)
    #line(length: 44pt, stroke: 3pt + accent)
  ]
  show heading.where(level: 2): set text(size: 19pt, fill: accent)
  show heading.where(level: 3): set text(size: 16.5pt)
  show strong: set text(fill: accent, weight: "bold")
  show link: set text(fill: accent)
  show raw: set text(font: ("Consolas", body-font), size: 0.8em, fill: accent)
  show raw.where(block: true): set block(fill: panel, inset: 14pt, radius: 7pt, width: 100%)
  show quote.where(block: true): it => note-card(title: "摘录", it.body)
  set table(inset: (x: 12pt, y: 11pt), stroke: (x, y) => (bottom: 0.5pt + divider, rest: none),
    fill: (x, y) => if y == 0 { accent } else if calc.odd(y) { panel } else { paper })
  show table: set text(size: 12.5pt)
  show table.cell.where(y: 0): set text(font: heading-font, fill: paper, weight: "bold")
  set figure(gap: 9pt)
  show figure.caption: set text(size: 11pt, fill: muted)

  // 封面在独立页面，背景与大号数字由矢量图形绘制。
  if title != none and $if(design-cover)$$design-cover$$else$false$endif$ {
    page(margin: (x: 0.75in, y: 0.7in), fill: paper, header: none, footer: none)[
      #place(right + top, dx: 24pt, dy: 45pt, circle(radius: 125pt, stroke: 1pt + divider))
      #place(right + top, dx: 38pt, dy: 76pt, circle(radius: 100pt, stroke: 1pt + divider))
      #place(right + top, dx: 62pt, dy: 108pt, circle(radius: 68pt, fill: panel))
      #text(font: "Georgia", size: 11pt, tracking: 2pt, fill: accent)[STORIES / IDEAS / DESIGN]
      #v(13pt)
      #line(length: 100%, stroke: 0.7pt + divider)
      #v(42pt)
      #tag[视觉排版手册]
      #v(25pt)
      #block(width: 86%)[
        #set par(leading: 0.32em)
        #text(font: heading-font, size: $if(design-cover-size)$$design-cover-size$pt$else$48pt$endif$, weight: "bold")[#title]
      ]
      #v(18pt)
      #block(width: 83%)[#text(size: 18pt, fill: muted)[#subtitle]]
      #v(34pt)
      #grid(columns: (1fr, 1fr, 1fr), column-gutter: 12pt,
        feature-card(number: "Aa", title: "字体层次")[标题、正文与引用],
        feature-card(number: "◌", title: "配色背景")[统一的视觉语言],
        feature-card(number: "↗", title: "图文排版")[卡片、图表与留白],
      )
      #v(1fr)
      #line(length: 100%, stroke: 0.7pt + divider)
      #v(13pt)
      #grid(columns: (1fr, auto),
        text(size: 11pt, fill: muted)[#if author != none [#author] #h(10pt) #if date != none [#date]],
        text(font: "Georgia", size: 10pt, fill: accent)[QUARTO + TYPST],
      )
    ]
  }

  set page(
    fill: paper,
    header: context {
      grid(columns: (1fr, auto),
        text(font: heading-font, size: 9pt, fill: muted)[#if title != none [#title]],
        text(font: "Georgia", size: 9pt, fill: accent)[READ / THINK / SHARE],
      )
      v(6pt)
      line(length: 100%, stroke: 0.6pt + divider)
    },
    footer: context {
      line(length: 100%, stroke: 0.6pt + divider)
      v(6pt)
      grid(columns: (1fr, auto),
        text(size: 9pt, fill: muted)[#if author != none [#author] #h(7pt) · #h(7pt) 文章设计],
        text(font: "Georgia", size: 11pt, fill: accent)[#counter(page).display("01")],
      )
    },
  )
  if toc {
    outline(title: toc-title, depth: toc-depth, indent: 1.1em)
    pagebreak()
  }
  doc
}
