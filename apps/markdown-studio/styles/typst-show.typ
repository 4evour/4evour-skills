#show: doc => designed-article(
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
$if(toc)$
  toc: $toc$,
$endif$
$if(toc-title)$
  toc-title: [$toc-title$],
$endif$
$if(toc-depth)$
  toc-depth: $toc-depth$,
$endif$
$if(fontsize)$
  fontsize: $fontsize$,
$endif$
  doc,
)
