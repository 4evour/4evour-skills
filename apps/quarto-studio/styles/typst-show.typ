#show: doc => article(
$if(title)$
  title: [$title$],
$endif$
$if(subtitle)$
  subtitle: [$subtitle$],
$endif$
$if(author)$
  author: [$for(author)$$author$$sep$、$endfor$],
$endif$
$if(date)$
  date: [$date$],
$endif$
  cover: $if(design-cover)$true$else$false$endif$,
  toc: $if(toc)$true$else$false$endif$,
  toc-title: [目录],
  toc-depth: 2,
  fontsize: $design-fontsize$pt,
  heading-size: $design-heading-size$pt,
  cover-size: $design-cover-size$pt,
  leading: $design-leading$em,
  spacing: $design-spacing$em,
  header: $if(design-header)$true$else$false$endif$,
  footer: $if(design-footer)$true$else$false$endif$,
  doc,
)
