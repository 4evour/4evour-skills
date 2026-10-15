#import "/styles/resources/runtime/showybox/2.0.4/showy.typ": showybox
#import "/styles/resources/runtime/codly/2.0.0/codly.typ" as codly

// 所有模板共用的中文、字体、段落、引用框与代码块控制。
#let body-with-quotes(c, body) = {
  if c.quote-style == "showybox" {
    show quote.where(block: true): it => showybox(
      frame: (body-color: c.panel, border-color: c.accent, thickness: 0.7pt, radius: 5pt, inset: 13pt),
      breakable: true,
      [#set text(font: (c.quote-font, c.body-font), fill: c.ink, size: 0.95em)
       #it.body],
    )
    body
  } else { body }
}


#let studio-content(c, body) = {
  set text(font: (c.body-font, "Source Han Sans SC", "Noto Serif SC"), size: c.fontsize, fill: c.ink, lang: "zh", region: "CN")
  set par(leading: c.leading, spacing: c.spacing, justify: false)
  show heading: set text(font: (c.heading-font, c.body-font))
  show heading.where(level: 1): set text(size: c.heading-size)
  show heading.where(level: 2): set text(size: c.heading-size * 0.72)
  show heading.where(level: 3): set text(size: c.heading-size * 0.60)
  show link: set text(fill: c.accent)
  show raw: set text(font: (c.code-font, "Sarasa Gothic SC", c.body-font), size: c.fontsize * 0.82)
  if c.code-style == "codly" {
    show: codly.theme("github-light")
    show: codly.set_(padding: 5pt, radius: 4pt)
    show raw.where(block: true): set block(fill: none, inset: 0pt, width: auto, radius: 0pt)
    show raw.where(block: true): it => {
      if it.text.split("\n").len() <= 12 { block(breakable: false, codly.new(it)) }
      else { codly.new(it) }
    }
    body-with-quotes(c, body)
  }
  else { body-with-quotes(c, body) }
}

#let studio-sidebar(body) = showybox(frame: (body-color: rgb("#F3F4F5"), border-color: rgb("#C8CDD1"), thickness: 0.6pt, radius: 4pt, inset: 12pt), breakable: true, body)
