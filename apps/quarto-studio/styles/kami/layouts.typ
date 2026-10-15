#import "/styles/page-background.typ": paper-background, blend
// Kami 风格的三套原生 Typst 版式。设计来源与许可见 resources/KAMI.md。
#let family(c) = (c.body-font, "Source Han Serif SC", "Noto Serif SC")
#let layout-name(c) = if c.layout == "brief" { "研究简报" } else if c.layout == "cards" { "分享卡片" } else { "阅读长文" }
#let small(c, body, color: none) = text(size: 8.5pt, fill: if color == none {c.muted} else {color}, weight: 400, body)
#let title-text(c, body, size: none) = text(font: (c.heading-font, c.body-font), weight: if c.heading-font == "TsangerJinKai02 W05" {400} else {500}, size: if size == none {c.heading-size} else {size}, body)

#let display-title(c, body, size) = layout(area => {
  let natural = measure(title-text(c, body, size: size)).width
  let lines = calc.max(1, calc.ceil(natural / area.width))
  let width = if lines > 1 {calc.min(area.width, natural / lines + size)} else {area.width}
  block(width: width, title-text(c, body, size: size))
})

#let tiles(columns: 2, ..cells) = grid(columns: (1fr,) * columns, column-gutter: 13pt, row-gutter: 12pt, ..cells.pos())
#let component-title(c, title, badge: none) = {
  if title != none or badge != none {
    block(sticky: true, below: 9pt)[
      #if badge != none [#box(fill: c.accent, radius: 3pt, inset: (x: 6pt, y: 3pt), text(size: 8pt, fill: c.paper)[#badge]) #h(6pt)]
      #if title != none [#text(font: (c.heading-font, c.body-font), size: 0.9em, fill: c.accent)[#title]]
    ]
  }
}
#let chips(c, ..items) = {
  for item in items.pos() {
    box(fill: blend(c.paper, c.accent, 0.075), stroke: 0.45pt + blend(c.paper, c.accent, 0.22), radius: 20pt,
      inset: (x: 10pt, y: 4.5pt), text(size: 0.8em, fill: c.accent, item))
    h(5pt)
  }
}
#let separator(c, label: none) = block(width: 100%, above: 17pt, below: 17pt, breakable: false)[
  #grid(columns: (1fr, auto, 1fr), column-gutter: 10pt, align: horizon,
    line(length: 100%, stroke: 0.6pt + c.divider),
    if label == none {square(size: 4pt, fill: c.accent)} else {text(size: 0.8em, fill: c.muted)[#label]},
    line(length: 100%, stroke: 0.6pt + c.divider))
]
#let panel(c, kind: "takeaway", title: none, label: none, value: none, body) = {
  let rounded = c.decoration == "soft"
  let editorial = c.decoration == "editorial"
  let radius = if rounded {9pt} else {0pt}
  let fill = blend(c.paper, c.accent, if rounded {0.055} else {0.04})
  let border = blend(c.paper, c.accent, 0.22)
  if kind == "lead" {
    block(width: 100%, above: 8pt, below: 18pt, breakable: true)[
      #set text(size: 1.12em, fill: c.muted)
      #set par(leading: 0.6em)
      #body
    ]
  } else if kind == "metric" {
    block(width: 100%, breakable: false, inset: if rounded {(x: 11pt, y: 12pt)} else {(top: 10pt, bottom: 12pt)},
      fill: if rounded {fill} else {none}, radius: radius,
      stroke: if rounded {0.5pt + border} else {(top: 1.2pt + c.accent)})[
      #if value != none [#title-text(c, value, size: c.fontsize * 2.05) #v(3pt)]
      #if label != none [#small(c, label) #v(6pt)]
      #set text(size: 0.85em, fill: c.muted)
      #body
    ]
  } else if kind == "pullquote" {
    block(width: 100%, above: 16pt, below: 16pt,
      inset: if rounded {(x: 17pt, y: 15pt)} else {(left: 15pt)}, radius: radius,
      fill: if rounded {fill} else {none}, stroke: if rounded {none} else {(left: 1.8pt + c.accent)})[
      #if editorial [#text(size: 28pt, fill: c.accent)[“] #v(-12pt)]
      #set text(font: (c.quote-font, c.body-font), size: 1.15em, fill: c.accent, weight: 400)
      #body
    ]
  } else if kind == "step" {
    block(width: 100%, above: 13pt, below: 13pt, inset: 14pt, radius: radius,
      fill: fill, stroke: (left: 2pt + c.accent), breakable: true)[
      #component-title(c, title, badge: if value == none {[01]} else {value})
      #body
    ]
  } else if kind in ("info", "alert", "success") {
    let tone = if kind == "alert" {rgb("#9D6638")} else if kind == "success" {rgb("#3C7459")} else {c.accent}
    if c.ink.luma().components().first() > c.paper.luma().components().first() {tone = blend(c.ink, tone, 0.35)}
    let local-c = c + (accent: tone)
    block(width: 100%, above: 13pt, below: 13pt, inset: 14pt, radius: radius,
      fill: blend(c.paper, tone, 0.055), stroke: (left: 2pt + tone), breakable: true)[
      #component-title(local-c, title, badge: if kind == "alert" {[!]} else if kind == "success" {[+]} else {[i]})
      #body
    ]
  } else if kind == "note" {
    block(width: 100%, above: 12pt, below: 12pt, inset: 12pt, fill: fill, radius: radius,
      stroke: if editorial {(top: 0.6pt + border, bottom: 0.6pt + border)} else {none}, breakable: true)[
      #component-title(c, title)
      #set text(size: 0.88em)
      #body
    ]
  } else {
    block(width: 100%, above: 14pt, below: 14pt, inset: (x: 15pt, y: 14pt), fill: fill,
      radius: radius, stroke: if rounded {0.6pt + border} else {(top: 1.1pt + c.accent)}, breakable: true)[
      #component-title(c, title, badge: if editorial {[要点]} else {none})
      #body
    ]
  }
}

// 按实际栏宽测量内容组，优先让每页两栏高度接近。过高单块交给原生分栏继续分页。
#let brief-columns(c, chunks, first-offset: 0pt) = layout(size => {
  let gutter = 23pt
  let width = (size.width - gutter) / 2
  let full = c.height - c.margin-y * 2 - 8pt
  let heights = chunks.map(chunk => measure(block(width: width, above: 0pt, below: 0pt, chunk)).height + 5pt)
  if heights.any(height => height > full) {
    columns(2, gutter: gutter, chunks.join(parbreak()))
  } else {
    let start = 0
    let capacity = calc.max(80pt, full - first-offset)
    while start < chunks.len() {
      let end = start
      let used = 0pt
      while end < chunks.len() and used + heights.at(end) <= capacity * 2 {
        used += heights.at(end)
        end += 1
      }
      let split = none
      while end > start and split == none {
        let score = 100000pt
        for i in range(start, end + 1) {
          let left = measure(block(width: width, chunks.slice(start, i).join(parbreak()))).height
          let right = measure(block(width: width, chunks.slice(i, end).join(parbreak()))).height
          if left <= capacity - 12pt and right <= capacity - 12pt and calc.abs(left - right) <= score {
            split = i
            score = calc.abs(left - right)
          }
        }
        if split == none {end -= 1}
      }
      if split == none {
        if capacity < full {colbreak(); capacity = full}
        else {
          columns(2, gutter: gutter, chunks.slice(start).join(parbreak()))
          start = chunks.len()
        }
      } else {
        block(width: 100%, breakable: false)[
          #grid(columns: (1fr, 1fr), column-gutter: gutter, align: top,
            chunks.slice(start, split).join(parbreak()), chunks.slice(split, end).join(parbreak()))
        ]
        start = end
        if start < chunks.len() {colbreak(); capacity = full}
      }
    }
  }
})

#let texture(c) = paper-background(width: c.width, height: c.height, style: c.background, strength: c.background-strength, paper: c.paper, accent: c.accent)

#let hero(c, title, subtitle, author, cover: false) = {
  let label = layout-name(c)
  if cover {
    page(header: none, footer: none)[
      #small(c, [私人阅读 / #label], color: c.accent)
      #v(1fr)
      #line(length: 48pt, stroke: 2pt + c.accent)
      #v(24pt)
      #set par(leading: 0.25em)
      #title-text(c, title, size: c.cover-size)
      #if subtitle != none [#v(20pt) #text(size: 1.1em, fill: c.muted)[#subtitle]]
      #v(1fr)
      #line(length: 100%, stroke: 0.6pt + c.divider)
      #v(12pt)
      #grid(columns: (1fr, auto), small(c, [#if author != none [#author]]), small(c, label))
    ]
  } else if title != none {
    if c.layout == "cards" {
      small(c, [FIELD NOTES / 私人阅读], color: c.accent)
      v(27pt)
      block(width: 97%)[#set par(leading: 0.24em)
#display-title(c, title, c.cover-size)]
      if subtitle != none [#v(14pt) #text(size: 1.05em, fill: c.muted)[#subtitle]]
      v(19pt)
      line(length: 42pt, stroke: 2pt + c.accent)
      v(15pt)
    } else if c.layout == "brief" {
      grid(columns: (1fr, auto), small(c, [RESEARCH / 研究简报], color: c.accent), small(c, [个人资料 · 阅读版]))
      v(14pt)
      block(width: 95%)[#set par(leading: 0.23em)
#title-text(c, title)]
      if subtitle != none [#v(8pt) #text(size: 0.95em, fill: c.muted)[#subtitle]]
      v(13pt)
      line(length: 100%, stroke: 1.4pt + c.accent)
      v(10pt)
    } else {
      grid(columns: (1fr, auto), small(c, [ESSAY / 阅读长文], color: c.accent), small(c, [#if author != none [#author]]))
      v(22pt)
      block(width: 97%)[#set par(leading: 0.28em)
#display-title(c, title, c.cover-size)]
      if subtitle != none [#v(14pt) #text(size: 1.04em, fill: c.muted)[#subtitle]]
      v(22pt)
      line(length: 100%, stroke: 0.7pt + c.divider)
      v(14pt)
    }
  }
}

#let flow(c, title: none, subtitle: none, author: none, cover: false, toc: false, continuation: false, front: [], main: [], chunks: ()) = {
  front
  if c.layout == "brief" {
    v(10pt)
    line(length: 100%, stroke: 0.6pt + c.divider)
    v(16pt)
    layout(size => {
      let first-offset = measure(block(width: size.width, front)).height + 42pt
      if not cover and not toc and not continuation {first-offset += measure(block(width: size.width, hero(c, title, subtitle, author))).height}
      brief-columns(c, chunks, first-offset: first-offset)
    })
  } else {main}
}

#let kami-document(c, title: none, subtitle: none, author: none, cover: false, toc: false, doc) = {
  set document(title: title)
  set text(font: family(c), size: c.fontsize, fill: c.ink, weight: 400, lang: "zh", region: "CN")
  set par(leading: c.leading, spacing: c.spacing, justify: false)
  set page(fill: c.paper, background: texture(c), numbering: none, header: none, footer: none)
  set list(indent: 0.9em, body-indent: 0.45em, spacing: 0.5em)
  set enum(indent: 1.15em, body-indent: 0.45em, spacing: 0.5em)
  set heading(numbering: none)
  show heading: set text(font: (c.heading-font, c.body-font), weight: if c.heading-font == "TsangerJinKai02 W05" {400} else {500})
  show heading.where(level: 1): it => block(above: 25pt, below: 14pt)[#title-text(c, it.body)]
  show heading.where(level: 2): it => context {
    let n = query(heading.where(level: 2).before(it.location(), inclusive: true)).len()
    let index = numbering("01", n)
    if c.layout == "cards" {
      pagebreak(weak: true)
      block(above: 15pt, below: 20pt, sticky: true)[
        #small(c, [#index / 阅读要点], color: c.accent)
        #v(13pt)
        #title-text(c, it.body, size: c.heading-size)
        #v(13pt)
        #line(length: 35pt, stroke: 1.6pt + c.accent)
      ]
    } else if c.layout == "brief" {
      block(above: 18pt, below: 10pt, sticky: true)[
        #text(size: 0.78em, fill: c.accent)[#index] #h(5pt) #title-text(c, it.body, size: c.fontsize * 1.32)
        #v(5pt) #line(length: 100%, stroke: 0.5pt + c.divider)
      ]
    } else {
      block(above: 27pt, below: 15pt, sticky: true)[
        #grid(columns: (30pt, 1fr), align: left + horizon,
          text(size: 10pt, fill: c.accent)[#index], title-text(c, it.body, size: c.fontsize * 1.55))
      ]
    }
  }
  show heading.where(level: 3): it => block(above: 17pt, below: 8pt, sticky: true)[#text(size: 1.08em, weight: 500, fill: c.accent)[#it.body]]
  show strong: set text(font: (c.heading-font, c.body-font), weight: if c.heading-font == "TsangerJinKai02 W05" {400} else {500})
  show link: set text(fill: c.accent)
  show quote.where(block: true): it => panel(c, kind: "pullquote", it.body)
  show raw: set text(font: (c.code-font, "JetBrains Mono", c.body-font), size: 0.78em)
  show raw.where(block: true): set block(width: 100%, fill: c.panel, inset: 11pt, radius: 0pt, breakable: true)
  set table(inset: (x: 7pt, y: 8pt), stroke: (x,y) => (bottom: 0.45pt + c.divider),
    fill: (x,y) => if y == 0 {c.panel} else {none})
  show table: set text(size: 0.86em)
  show table.cell.where(y: 0): set text(weight: 500, fill: c.accent)
  set figure(gap: 8pt)
  show figure.caption: set text(size: 0.78em, fill: c.muted)
  if cover and title != none {hero(c, title, subtitle, author, cover: true)}
  set page(
    header: if c.header {[
      #grid(columns: (1fr, auto), small(c, layout-name(c)), small(c, [私人阅读]))
      #v(5pt) #line(length: 100%, stroke: 0.45pt + c.divider)
    ]} else {none},
    footer: if c.footer {context [
      #line(length: 100%, stroke: 0.45pt + c.divider) #v(6pt)
      #grid(columns: (1fr, auto), small(c, [#if author != none [#author] #h(6pt) #layout-name(c)]),
        small(c, [#counter(page).display("01") / #counter(page).final().first()]))
    ]} else {none},
  )
  if not cover {hero(c, title, subtitle, author)}
  if toc {outline(title: [目录], indent: 1em, depth: 2); pagebreak()}
  doc
}
