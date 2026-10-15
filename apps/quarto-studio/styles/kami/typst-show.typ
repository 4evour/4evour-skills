#show: doc => kami-document(c,
  title: $if(title)$[$title$]$else$none$endif$,
  subtitle: $if(subtitle)$[$subtitle$]$else$none$endif$,
  author: $if(author)$[$for(author)$$author$$sep$、$endfor$]$else$none$endif$,
  cover: $if(design-cover)$true$else$false$endif$,
  toc: $if(toc)$true$else$false$endif$,
  doc,
)
