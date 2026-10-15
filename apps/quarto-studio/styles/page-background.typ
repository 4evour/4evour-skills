// 同一组参数用于实际 PDF 纸面与预览；图形全部为矢量。
#let blend(paper, accent, amount) = color.mix((paper, 100% - amount * 100%), (accent, amount * 100%))
#let paper-background(width: 612pt, height: 792pt, style: "plain", strength: 0.22, paper: white, accent: black) = {
  let fine = blend(paper, accent, strength * 0.38)
  let faint = blend(paper, accent, strength * 0.15)
  if style == "grid" {
    for x in range(0, int(width / 24pt) + 1) {place(top + left, dx: x * 24pt, line(start: (0pt, 0pt), end: (0pt, height), stroke: 0.35pt + fine))}
    for y in range(0, int(height / 24pt) + 1) {place(top + left, dy: y * 24pt, line(length: width, stroke: 0.35pt + fine))}
  } else if style == "dots" {
    for x in range(0, int(width / 20pt) + 1) {for y in range(0, int(height / 20pt) + 1) {
      place(top + left, dx: x * 20pt, dy: y * 20pt, circle(radius: 0.6pt, fill: fine))
    }}
  } else if style == "ruled" {
    for y in range(0, int(height / 25pt) + 1) {place(top + left, dy: y * 25pt, line(length: width, stroke: 0.4pt + fine))}
    place(top + left, dx: 29pt, line(start: (0pt, 0pt), end: (0pt, height), stroke: 0.5pt + fine))
  } else if style == "linen" {
    for y in range(0, int(height / 6pt) + 1) {place(top + left, dy: y * 6pt, line(length: width, stroke: 0.25pt + faint))}
    for x in range(0, int(width / 6pt) + 1) {place(top + left, dx: x * 6pt, line(start: (0pt, 0pt), end: (0pt, height), stroke: 0.18pt + faint))}
    for n in range(0, 260) {
      let x = calc.rem(n * 97 + 31, int(width / 1pt)) * 1pt
      let y = calc.rem(n * 193 + 53, int(height / 1pt)) * 1pt
      place(top + left, dx: x, dy: y, line(length: 1.6pt, angle: 25deg, stroke: 0.4pt + fine))
    }
  } else if style == "wash" {
    place(top + left, rect(width: width, height: height,
      fill: gradient.linear(paper, paper, blend(paper, accent, strength * 0.5), angle: 45deg)))
  } else if style == "frame" {
    place(top + left, dx: 17pt, dy: 17pt, rect(width: width - 34pt, height: height - 34pt, stroke: 0.7pt + fine, fill: none))
    place(top + left, dx: 17pt, dy: 17pt, line(length: 38pt, stroke: 1.4pt + blend(paper, accent, strength)))
    place(bottom + right, dx: -17pt, dy: -17pt, line(length: 38pt, stroke: 1.4pt + blend(paper, accent, strength)))
  }
}
