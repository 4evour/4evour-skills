#import "/styles/page-background.typ": paper-background
#import "/styles/resource-common.typ": studio-content, studio-sidebar
#let palette = (
  paper: $if(design-paper)$rgb(content-to-string([$design-paper$]))$else$rgb("#F6F2EA")$endif$,
  ink: $if(design-ink)$rgb(content-to-string([$design-ink$]))$else$rgb("#202B36")$endif$,
  accent: $if(design-accent)$rgb(content-to-string([$design-accent$]))$else$rgb("#B7472A")$endif$,
  muted: $if(design-muted)$rgb(content-to-string([$design-muted$]))$else$rgb("#6D747D")$endif$,
  panel: $if(design-panel)$rgb(content-to-string([$design-panel$]))$else$rgb("#ECE7DD")$endif$,
  divider: $if(design-divider)$rgb(content-to-string([$design-divider$]))$else$rgb("#D8D0C2")$endif$,
)
#let paper = palette.paper
#let ink = palette.ink
#let accent = palette.accent
#let muted = palette.muted
#let panel = palette.panel
#let divider = palette.divider
#let heading-font = "$design-heading-font$"
#let body-font = "$design-body-font$"
#let quote-font = "$design-quote-font$"
#let page-w = $design-page-width$pt
#let page-h = $design-page-height$pt
#let texture = paper-background(width: page-w, height: page-h, style: "$design-background$", strength: $design-background-strength$, paper: paper, accent: accent)

#let article(title: none, subtitle: none, author: none, date: none,
  cover: false, toc: false, toc-title: "目录", toc-depth: 2, fontsize: 16.5pt,
  heading-size: 28pt, cover-size: 42pt, leading: 0.65em, spacing: 0.8em,
  header: true, footer: true, doc) = {
  set document(title: title)
  if author != none { set document(author: content-to-string(author)) }
  set text(font: (body-font, "Microsoft YaHei", "Noto Serif SC"), size: fontsize, fill: ink, lang: "zh", region: "CN")
  set par(leading: leading, spacing: spacing, justify: false)
  set page(fill: paper, background: texture, numbering: none, header: none, footer: none)
  set heading(numbering: none)
  show heading: set text(font: (heading-font, body-font), fill: ink, weight: "bold")
  show heading.where(level: 1): it => block(above: 8pt, below: 18pt)[
    #text(size: heading-size)[#it.body]
    #v(9pt)
    #line(length: 40pt, stroke: 2.2pt + accent)
  ]
  show heading.where(level: 2): set text(size: heading-size * 0.72, fill: accent)
  show heading.where(level: 3): set text(size: heading-size * 0.60, fill: ink)
  show strong: set text(fill: accent, weight: "bold")
  show link: set text(fill: accent)
  show raw: set text(font: ("Consolas", "DejaVu Sans Mono", body-font), size: 0.79em)
  show raw.where(block: true): set block(width: 100%, fill: panel, radius: 6pt, inset: 13pt)
  show quote.where(block: true): it => block(
    width: 100%, inset: (x: 15pt, y: 13pt), radius: 6pt, fill: panel,
    stroke: (left: 2pt + accent, rest: none), above: 14pt, below: 14pt,
  )[
    #text(font: (quote-font, body-font), fill: muted, size: 0.95em)[#it.body]
  ]
  set table(inset: (x: 10pt, y: 10pt),
    stroke: (x, y) => (bottom: 0.45pt + divider, rest: none),
    fill: (x, y) => if y == 0 { panel } else if calc.odd(y) { paper } else { panel })
  show table: set text(size: 0.82em)
  show table.cell.where(y: 0): set text(font: (heading-font, body-font), weight: "bold", fill: accent)
  set figure(gap: 9pt)
  show figure.caption: set text(size: 0.75em, fill: muted)
  if cover and title != none {
    page(header: none, footer: none)[
      #place(top + right, dy: 32pt, circle(radius: 94pt, stroke: 0.8pt + divider))
      #place(top + right, dx: 18pt, dy: 68pt, circle(radius: 67pt, fill: panel))
      #v(30pt)
      #text(size: 11pt, tracking: 1.5pt, fill: accent)[QUARTO / TYPST]
      #v(55pt)
      #block(width: 93%)[
        #set par(leading: 0.30em)
        #text(font: (heading-font, body-font), weight: "bold", size: cover-size)[#title]
      ]
      #if subtitle != none [#v(22pt) #text(size: fontsize * 1.05, fill: muted)[#subtitle]]
      #v(1fr)
      #line(length: 100%, stroke: 0.7pt + divider)
      #v(12pt)
      #grid(columns: (1fr, auto),
        text(size: 10pt, fill: muted)[#if author != none [#author]],
        text(size: 10pt, fill: muted)[#if date != none [#date]],
      )
    ]
  }
  set page(
    header: if header { context {
      grid(columns: (1fr, auto),
        text(size: 9pt, fill: muted)[#if title != none [#title]],
        text(size: 9pt, fill: accent)[阅读笔记],
      )
      v(6pt)
      line(length: 100%, stroke: 0.6pt + divider)
    } } else { none },
    footer: if footer { context {
      line(length: 100%, stroke: 0.6pt + divider)
      v(6pt)
      grid(columns: (1fr, auto),
        text(size: 9pt, fill: muted)[#if author != none [#author]],
        text(size: 10pt, fill: accent)[#counter(page).display("01")],
      )
    } } else { none },
  )
  if toc {
    outline(title: toc-title, depth: toc-depth, indent: 1.1em)
    pagebreak()
  }
  studio-content((body-font: body-font, heading-font: heading-font, quote-font: quote-font,
    code-font: "$design-code-font$", code-style: "$design-code-style$", quote-style: "$design-quote-style$",
    fontsize: fontsize, heading-size: heading-size, leading: leading, spacing: spacing,
    ink: ink, accent: accent, panel: panel), doc)
}
