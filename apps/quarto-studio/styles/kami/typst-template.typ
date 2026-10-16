#import "/styles/kami/layouts.typ": kami-document, panel, tiles, flow, chips, separator
#let c = (
  layout: "$design-layout$", body-font: "$design-body-font$", heading-font: "$design-heading-font$",
  quote-font: "$design-quote-font$", code-font: "$design-code-font$",
  fontsize: $design-fontsize$pt, heading-size: $design-heading-size$pt,
  cover-size: $design-cover-size$pt, leading: $design-leading$em, spacing: $design-spacing$em,
  paper: rgb(content-to-string([$design-paper$])), ink: rgb(content-to-string([$design-ink$])), accent: rgb(content-to-string([$design-accent$])),
  muted: rgb(content-to-string([$design-muted$])), panel: rgb(content-to-string([$design-panel$])), divider: rgb(content-to-string([$design-divider$])),
  width: $design-page-width$pt, height: $design-page-height$pt,
  margin-x: $design-margin-x$pt, margin-y: $design-margin-y$pt,
  image-path: $if(design-background-image)$"$design-background-image$"$else$none$endif$, image-opacity: $if(design-background-image-opacity)$$design-background-image-opacity$$else$0.48$endif$, image-fit: "$if(design-background-image-fit)$$design-background-image-fit$$else$cover$endif$", image-scope: "$if(design-background-image-scope)$$design-background-image-scope$$else$all$endif$",
  background: "$design-background$", background-strength: $design-background-strength$, decoration: "$design-decoration$", header: $if(design-header)$true$else$false$endif$,
  footer: $if(design-footer)$true$else$false$endif$,
)
#let kami-panel = panel.with(c)
#let kami-tiles = tiles
#let kami-chips = chips.with(c)
#let kami-separator = separator.with(c)
#let kami-flow = flow.with(c,
  title: $if(title)$[$title$]$else$none$endif$,
  subtitle: $if(subtitle)$[$subtitle$]$else$none$endif$,
  author: $if(author)$[$for(author)$$author$$sep$、$endfor$]$else$none$endif$,
  cover: $if(design-cover)$true$else$false$endif$,
  toc: $if(toc)$true$else$false$endif$,
)
