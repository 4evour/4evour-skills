#import "/styles/page-background.typ": paper-background
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

#import "/styles/resource-common.typ": studio-content, studio-sidebar
$if(studio-dept-news)$
#import "/styles/resources/runtime/dashing-dept-news/0.1.1/lib.typ": newsletter, article as dept-sidebar
#let studio-sidebar(body) = dept-sidebar(body)
$elseif(studio-tufte)$
#import "/styles/resources/runtime/tufte.typ": tufte, note
$elseif(studio-orange-book)$
#import "/styles/resources/runtime/orange-book/0.7.1/lib.typ": book
$elseif(studio-vibrant-color)$
#import "/styles/resources/runtime/vibrant-color/0.2.1/vibrant-color.typ": vibrant-color
$elseif(studio-modern-technique-report)$
#import "/styles/resources/runtime/modern-technique-report/0.1.0/lib.typ": modern-technique-report
$elseif(studio-ilm)$
#import "/styles/resources/runtime/ilm/2.1.1/lib.typ": ilm
$elseif(studio-fiction)$
#import "/styles/resources/runtime/wonderous-book/0.1.2/lib.typ": book
$endif$

#let article(title: none, subtitle: none, author: none, date: none,
  cover: false, toc: false, toc-title: "目录", toc-depth: 2, fontsize: 16.5pt,
  heading-size: 28pt, cover-size: 42pt, leading: 0.65em, spacing: 0.8em,
  header: true, footer: true, doc) = {
  let c = (title: title, subtitle: subtitle, author: author,
    body-font: body-font, heading-font: heading-font, quote-font: quote-font,
    code-font: "$design-code-font$", code-style: "$design-code-style$", quote-style: "$design-quote-style$",
    paper: paper, ink: ink, accent: accent, panel: panel, muted: muted, divider: divider,
    width: page-w, height: page-h, margin-x: $design-margin-x$pt, margin-y: $design-margin-y$pt,
    fontsize: fontsize, heading-size: heading-size, cover-size: cover-size,
    leading: leading, spacing: spacing, cover: cover, toc: toc, header: header, footer: footer,
  )
  set document(title: title, author: if author == none { "" } else { content-to-string(author) })
  set text(font: (body-font, "Source Han Sans SC"), size: fontsize, fill: ink, lang: "zh", region: "CN")
  set page(width: page-w, height: page-h, margin: (x: c.margin-x, y: c.margin-y), fill: paper, background: texture)
  let authors = if author == none { ("",) } else { (content-to-string(author),) }
  let content = studio-content(c, doc)
$if(studio-dept-news)$
  newsletter(studio: c, title: title, edition: subtitle, publication-info: author, content)
$elseif(studio-tufte)$
  tufte(studio: c, title: title, subtitle: subtitle, date: if date == none { [] } else { date },
    font: (body-font, "Source Han Serif SC"), sansfont: (heading-font, "Source Han Sans SC"),
    fontsize: fontsize, lang: "zh", region: "CN", toc: toc, content)
$elseif(studio-orange-book)$
  book(studio: c, title: title, subtitle: if subtitle == none { [] } else { subtitle },
    author: authors.first(), copyright: none,
    width: page-w, height: page-h, margin: (x: c.margin-x, y: c.margin-y),
    main-color: accent, lang: "zh", font-size: fontsize, first-line-indent: false, heading-style: 1,
    supplement-chapter: "章", supplement-part: "部分", content)
$elseif(studio-vibrant-color)$
  vibrant-color(studio: c, title: title, authors: authors, sub-authors: "", subject: "阅读文档",
    description: if subtitle == none { [] } else { subtitle }, lang: "zh", theme: "$design-vibrant-theme$", content)
$elseif(studio-modern-technique-report)$
  modern-technique-report(studio: c, title: title, subtitle: if subtitle == none { [] } else { subtitle },
    author: if author == none { [] } else { author }, date: if date == none { [] } else { date },
    series: "专题文档", background: rect(width: page-w, height: page-h * 0.34, fill: accent),
    theme-color: accent, font: body-font, title-font: heading-font, content)
$elseif(studio-ilm)$
  ilm(studio: c, title: title, authors: authors,
    cover-page: if cover { "use-ilm-default" } else { none },
    table-of-contents: if toc { outline(title: [目录], depth: 2) } else { none },
    raw-text: (font: ("$design-code-font$", body-font), size: 0.78em),
    footer: if footer { "page-number-center" } else { none },
    external-link-circle: false, chapter-pagebreak: false, content)
$elseif(studio-fiction)$
  book(studio: c, title: title, author: authors.first(), content)
$endif$
}
