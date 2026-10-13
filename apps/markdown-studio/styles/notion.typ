// 浅色表头、隔行底色和细分隔线，保持正式长文的阅读节奏。
#show table.cell.where(y: 0): set text(weight: "bold", fill: rgb("#37352F"))
#show table: set text(size: 0.92em)
#set table(
  stroke: (x, y) => {
    if y == 0 {
      (bottom: 0.8pt + rgb("#E3E2E0"), rest: 0pt)
    } else {
      (bottom: 0.5pt + rgb("#EFEFEF"), rest: 0pt)
    }
  },
  fill: (x, y) => {
    if y == 0 { rgb("#F7F6F3") }
    else if calc.odd(y) { rgb("#FBFBFA") }
    else { white }
  },
  inset: (x: 10pt, y: 8pt),
)
#set par(leading: 0.85em, justify: false)
