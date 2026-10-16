#import "/styles/resources/runtime/drafting/0.2.2/drafting.typ": *

#let to-string(content) = {
  if content.has("text") {
    content.text
  } else if content.has("children") {
    content.children.map(to-string).join("")
  } else if content.has("body") {
    to-string(content.body)
  } else if content == [ ] {
    " "
  }
}

#let to-label(string) = {
  label("<" + string + ">")
}

// Some definitions presupposed by pandoc's typst output.
#let blockquote(body) = [
  #set text( size: 0.92em )
  #block(inset: (left: 1.5em, top: 0.2em, bottom: 0.2em))[#body]
]

#let horizontalrule = [
  #line(start: (25%,0%), end: (75%,0%))
]

#let endnote(num, contents) = [
  #stack(dir: ltr, spacing: 3pt, super[#num], contents)
]

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

// Some quarto-specific definitions.

#show raw.where(block: true): block.with(
    fill: luma(230),
    width: 100%,
    inset: 8pt,
    radius: 2pt
  )

#show raw.where(block: true): set align(left)

#let block_with_new_content(old_block, new_content) = {
  let d = (:)
  let fields = old_block.fields()
  fields.remove("body")
  if fields.at("below", default: none) != none {
    // TODO: this is a hack because below is a "synthesized element"
    // according to the experts in the typst discord...
    fields.below = fields.below.amount
  }
  return block.with(..fields)(new_content)
}

#let empty(v) = {
  if type(v) == "string" {
    // two dollar signs here because we're technically inside
    // a Pandoc template :grimace:
    v.matches(regex("^\\s*$$")).at(0, default: none) != none
  } else if type(v) == "content" {
    if v.at("text", default: none) != none {
      return empty(v.text)
    }
    for child in v.at("children", default: ()) {
      if not empty(child) {
        return false
      }
    }
    return true
  }

}

// Subfloats
// This is a technique that we adapted from https://github.com/tingerrr/subpar/
#let quartosubfloatcounter = counter("quartosubfloatcounter")

#let quarto_super(
  kind: str,
  caption: none,
  label: none,
  supplement: str,
  position: none,
  subrefnumbering: "1a",
  subcapnumbering: "(a)",
  body,
) = {
  context {
    let figcounter = counter(figure.where(kind: kind))
    let n-super = figcounter.get().first() + 1
    set figure.caption(position: position)
    [#figure(
      kind: kind,
      supplement: supplement,
      caption: caption,
      {
        show figure.where(kind: kind): set figure(numbering: _ => numbering(subrefnumbering, n-super, quartosubfloatcounter.get().first() + 1))
        show figure.where(kind: kind): set figure.caption(position: position)

        show figure: it => {
          let num = numbering(subcapnumbering, n-super, quartosubfloatcounter.get().first() + 1)
          show figure.caption: it => {
            num.slice(2) // I don't understand why the numbering contains output that it really shouldn't, but this fixes it shrug?
            [ ]
            it.body
          }

          quartosubfloatcounter.step()
          it
          counter(figure.where(kind: it.kind)).update(n => n - 1)
        }

        quartosubfloatcounter.update(0)
        body
      }
    )#label]
  }
}

// callout rendering
// this is a figure show rule because callouts are crossreferenceable
#show figure: it => {
  if type(it.kind) != "string" {
    return it
  }
  let kind_match = it.kind.matches(regex("^quarto-callout-(.*)")).at(0, default: none)
  if kind_match == none {
    return it
  }
  let kind = kind_match.captures.at(0, default: "other")
  kind = upper(kind.first()) + kind.slice(1)
  // now we pull apart the callout and reassemble it with the crossref name and counter

  // when we cleanup pandoc's emitted code to avoid spaces this will have to change
  let old_callout = it.body.children.at(1).body.children.at(1)
  let old_title_block = old_callout.body.children.at(0)
  let old_title = old_title_block.body.body.children.at(2)

  // TODO use custom separator if available
  let new_title = if empty(old_title) {
    [#kind #it.counter.display()]
  } else {
    [#kind #it.counter.display(): #old_title]
  }

  let new_title_block = block_with_new_content(
    old_title_block,
    block_with_new_content(
      old_title_block.body,
      old_title_block.body.body.children.at(0) +
      old_title_block.body.body.children.at(1) +
      new_title))

  block_with_new_content(old_callout,
    new_title_block +
    old_callout.body.children.at(1))
}

// 2023-10-09: #fa-icon("fa-info") is not working, so we'll eval "#fa-info()" instead
#let callout(body: [], title: "Callout", background_color: rgb("#dddddd"), icon: none, icon_color: black) = {
  block(
    breakable: false,
    fill: background_color,
    stroke: (paint: icon_color, thickness: 0.5pt, cap: "round"),
    width: 100%,
    radius: 2pt,
    block(
      inset: 1pt,
      width: 100%,
      below: 0pt,
      block(
        fill: background_color,
        width: 100%,
        inset: 8pt)[#text(icon_color, weight: 900)[#icon] #title]) +
      if(body != []){
        block(
          inset: 1pt,
          width: 100%,
          block(fill: white, width: 100%, inset: 8pt, body))
      }
    )
}


// pandoc handling
#let sansfont = "Source Han Sans SC"

/* Sidenotes
Display content in the right margin with the `note()` function.
Takes 2 optional keyword and 1 required argument:
  - `dy: length` Adjust the vertical position as required (default `0pt`).
  - `numbered: bool` Display a footnote-style number in text and in the note (default `true`).
  - `content: content` The content of the note.
*/
#let notecounter = counter("notecounter")
#let note(dy: -2em, numbered: true, content) = context {
  if numbered {
    notecounter.step()
    text(weight: "bold", super(notecounter.display()))
  }
  text(
    size: 9pt,
    font: sansfont,
    margin-note(
      if numbered {
        text(
          weight: "bold",
          font: "Lucida Bright",
          size: 11pt,
          {
            super(notecounter.display())
            text(size: 9pt, " ")
          },
        )
        content
      } else {
        content
      },
      dy: dy,
    ),
  )
}

/* Sidenote citation
Display a short citation in the right margin with the `notecite()` function.
Takes 2 optional keyword and 1 required argument.
  - `dy: length` Adjust the vertical position as required (default `0pt`).
  - `supplement: content` Supplement for the in-text citation (e.g., `p.~7`), (default `none`).
  - `key: label` The bibliography entry's label.

CAUTION: if no bibliography is defined, then this function will not display anything.
*/
#let notecite(dy: -2em, supplement: none, key) = (
  context {
    let elems = query(bibliography)
    if elems.len() > 0 {
      if type(key) == label {
        cite(key)
      } else {
      let (key, supplement, form, style) = key.fields()
      cite(key, supplement: supplement, style: "ieee")
      note(
        cite(key, form: "full", style: "short_ref.csl"),
        dy: dy,
        numbered: false,
      )
      }
    }
  }
)

#let wideblock(content) = block(width: 100% + 2.5in, content)

#let tufte(
  studio: (:),
  title: none,
  subtitle: none,
  shorttitle: none,
  document-number: none,
  authors: none,
  date: datetime.today(),
  abstract: none,
  publisher: none,
  abstract-title: none,
  margin: (left: 1in, right: 3.5in, y: 1.5in),
  paper: "us-letter",
  lang: "en",
  region: "US",
  font: (),
  fontsize: 11pt,
  codefont: "DejaVu Sans Mono",
  sansfont: "Gill Sans MT",
  sectionnumbering: none,
  toc: false,
  toc_title: none,
  toc_depth: none,
  toc_indent: 1.5em,
  draft: false,
  footer-content: none,
  distribution: none,
  doc,
) = {

  // Document metadata
  if authors != none {
    set document(
      title: title,
      author: authors.map(author => to-string(author.name)),
    )
  } else {
    set document(title: title)
  }

  // Just a suttle lightness to decrease the harsh contrast
  set text(fill: studio.ink)

  // Tables and figures
  show figure: set figure.caption(separator: [.#h(0.5em)])
  show figure.caption: set align(left)
  show figure.caption: set text(font: sansfont)

  show figure.where(kind: table): set figure.caption(position: top)
  show figure.where(kind: table): set figure(numbering: "I")
  show figure.where(kind: "quarto-float-tbl"): set figure.caption(position: top)
  show figure.where(kind: "quarto-float-tbl"): set figure(numbering: "I")

  show figure.where(kind: image): set figure(
    supplement: [Figure],
    numbering: "1",
  )
  show figure.where(kind: "quarto-float-fig"): set figure(
    supplement: [Figure],
    numbering: "1",
  )

  show figure.where(kind: raw): set figure.caption(position: top)
  show figure.where(kind: raw): set figure(supplement: [Code], numbering: "1")
  show raw: set text(font: studio.code-font, size: 10pt)

  // Equations
  set math.equation(numbering: "(1)")
  show math.equation: set block(spacing: 0.65em)

  show link: underline

  // Lists
  set enum(
    indent: 1em,
    body-indent: 1em,
  )
  show enum: set par(justify: false)
  set list(
    indent: 1em,
    body-indent: 1em,
  )
  show list: set par(justify: false)

  // Headings
  set heading(numbering: none)
  show heading.where(level: 1): it => {
    v(2em, weak: true)
    text(size: 14pt, weight: "bold", it)
    v(1em, weak: true)
  }

  show heading.where(level: 2): it => {
    v(1.3em, weak: true)
    text(size: 13pt, weight: "regular", style: "italic", it)
    v(1em, weak: true)
  }

  show heading.where(level: 3): it => {
    v(1em, weak: true)
    text(size: fontsize, style: "italic", weight: "thin", it)
    v(0.65em, weak: true)
  }

  // show heading: it => {
  //   if it.level <= 3 {
  //     it
  //   } else { }
  // }

  // Page setup
  set page(
    width: studio.width, height: studio.height, fill: studio.paper,
    margin: (left: studio.margin-x, right: studio.margin-x + 110pt, y: studio.margin-y),
    header: context {
      set text(font: sansfont)
      block(
        width: 100% + 110pt,
        {
          if counter(page).get().first() > 1 {
            if document-number != none {
              document-number
            }
            h(1fr)
            if shorttitle != none {
              upper(shorttitle)
            } else {
              upper(title)
            }
            if publisher != none {
              linebreak()
              h(1fr)
              upper(publisher)
            }
          }
        },
      )
    },
    footer: context {
      set text(font: sansfont, size: 8pt)
      block(
        width: 100% + 110pt,
        {
          if counter(page).get().first() == 1 {
            if type(footer-content) == array {
              footer-content.at(0)
              linebreak()
            } else {
              footer-content
              linebreak()
            }
            if draft [
              Draft document, #date.
            ]
            if distribution != none [
              Distribution limited to #distribution.
            ]
          } else {
            if type(footer-content) == array {
              footer-content.at(1)
              linebreak()
            } else {
              footer-content
              linebreak()
            }
            if draft [
              Draft document, #date.
            ]
            if distribution != none [
              Distribution limited to #distribution.
            ]
            linebreak()
            [Page #counter(page).display()]
          }
        },
      )
    },
    background: if studio.at("image-path", default: none) != none { studio.texture } else if draft {
      rotate(
        45deg,
        text(font: sansfont, size: 200pt, fill: rgb("FFEEEE"))[DRAFT],
      )
    },
  )

  set par(
    // justify: true,
    leading: 0.65em,
    first-line-indent: 1em
  )
  set par(spacing: 0.65em)


  // frontmatter
  if title != none {
    wideblock({
      set text(
        hyphenate: false,
        size: 20pt,
        font: sansfont,
      )
      set par(
        justify: false,
        leading: 0.2em,
        first-line-indent: 0pt,
      )
      upper(title)
      set text(size: fontsize)
      v(-0.65em)
      upper(subtitle)
    })
  }

  if authors != none {
    wideblock({
      set text(font: sansfont, size: fontsize)
      v(1em)
      for i in range(calc.ceil(authors.len() / 3)) {
        let end = calc.min((i + 1) * 3, authors.len())
        let is-last = authors.len() == end
        let slice = authors.slice(i * 3, end)
        grid(
          columns: slice.len() * (1fr,),
          gutter: fontsize,
          ..slice.map(author => align(
            left,
            {
              upper(author.name)
              if "university" in author [
                \ #author.university
              ]
              if "email" in author [
                \ #to-string(author.email)
              ]
            },
          ))
        )

        if not is-last {
          v(16pt, weak: true)
        }
      }
    })
  }

  if date != none {
    upper(date)
    linebreak()
    if document-number != none {
      document-number
    }
  }

  if abstract != none {
    wideblock({
      set text(font: sansfont)
      set par(hanging-indent: 3em)
      h(3em)
      abstract
    })
  }

  if toc {
    wideblock({
      v(1em)
      set text(font: sansfont)
      outline(indent: 1em, title: none, depth: 2)
    })
  }

  // Finish setting up sidenotes
  set-page-properties()
  set-margin-note-defaults(
    stroke: none,
    side: right,
    margin-right: 110pt,
    margin-left: studio.margin-x,
  )

  // Body text
  set text(
    lang: lang,
    region: region,
    font: font,
    style: "normal",
    weight: "regular",
    hyphenate: true,
    size: fontsize,
  )

  show cite.where(form: "prose"): notecite

  doc

}

#set table(
  inset: 6pt,
  stroke: none,
)
