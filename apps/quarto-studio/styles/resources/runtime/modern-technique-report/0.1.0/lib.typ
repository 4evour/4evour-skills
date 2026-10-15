// Quarto Studio 中文及控制台适配；原始源码、许可见 resources/upstream。
#let modern-technique-report(
  title: [Report Title],
  subtitle: [Report Subtitle],
  series: [Report Series],
  author: [Report Author],
  date: [Report Date],
  background: "bg.jpg",
  theme-color: rgb(128, 128, 128),
  font: "New Computer Modern",
  title-font: "Noto Sans",
  studio: (:),
  doc
) = {
  set text(font: font, size: studio.fontsize, fill: studio.ink, lang: "zh")

  let bg-color = theme-color.lighten(90%)
  let font-color = theme-color.darken(30%)

  set heading(
    numbering: 
      (..nums) => [
        #nums.pos().map(str).join(".")
        #h(0.5em)
        #box(width: 1.2pt, height: 1.1em, fill: gray.darken(20%), baseline: 20%)
        #h(0.2em)
      ]
  )
  show heading: it => text(fill: font-color, font: title-font)[#it #v(0.5em)]
  show heading.where(level: 1): set text(15pt)
  show heading.where(level: 2): set text(12pt)
  show heading.where(level: 1): it => {pagebreak(weak: true);it}

  if studio.cover {
  // Cover begin

  // Background
  place(
    bottom + center,
    dy: 71pt
  )[#scale(x: 132%, y: 132%, origin: bottom)[#background]]

  place(
    top + left,
    dy: -71pt,
    dx: -71pt
  )[
    #polygon(
      fill: rgb(254, 254, 254),
      (0pt, 0pt),
      (596pt, 0pt),
      (596pt, 650pt),
      (0pt, 550pt),
    )
  ]

  // Series
  box(fill: theme-color, width: 3pt, height: 43pt)
  h(5pt) 
  box[#par(leading: 0.65em)[#text(size: 15pt)[*#series*]] #v(5pt)]

  v(100pt)

  // Titles & Author
  align(center)[
    #set par(leading: 1em)
    
    #text(25pt, tracking: 2pt, font: title-font)[*#title*]

    #text(15pt)[#subtitle]

    #v(25pt)
    
    #text(15pt)[#author]
  ]

  v(4em)
  text(size: 14pt)[#align(right)[#date]]

  pagebreak()

  }
  // Cover end

  if studio.toc {
  // Outline begin

  show outline.entry.where(level: 1): set text(13pt, font: title-font, weight: "bold", fill: font-color)
  set outline.entry(fill: repeat[.])
  outline(
    title: [目录], depth: 2
  )

  pagebreak()
  }
  // Outline end

  doc
}
