// Import from our fork of dashing-dept-news with figure-caption-style option
// TODO: Change to @preview/dashing-dept-news once upstreamed
#import "@local/dashing-dept-news:0.1.1": newsletter, article

// Helper: convert hero-image from {path, caption} to {image, caption}
#let adapt-hero-image(hero-image) = (
  image: image(hero-image.path, width: 14cm),
  caption: hero-image.caption
)
