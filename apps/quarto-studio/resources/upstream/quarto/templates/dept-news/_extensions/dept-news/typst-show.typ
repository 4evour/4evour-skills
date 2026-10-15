#show: newsletter.with(
$if(title)$
  title: "$title$",
$endif$
$if(edition)$
  edition: [$edition$],
$endif$
$if(hero-image)$
  hero-image: adapt-hero-image((path: "$hero-image.path$", caption: [$hero-image.caption$])),
$endif$
$if(publication-info)$
  publication-info: [$publication-info$],
$endif$
  figure-caption-style: "academic",
)
