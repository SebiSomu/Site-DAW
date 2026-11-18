export interface Shelf {
  slug: string
  name: string
  note: string
  image: string
  imageAlt: string
}

export const SHELVES: Shelf[] = [
  {
    slug: 'jams',
    name: 'Jams',
    note: 'Sun-ripened fruit, cooked slowly until the whole house smells like summer.',
    image: '/images/plates/strawberry.jpg',
    imageAlt: 'Watercolour of a single ripe strawberry on its stem, painted in 1889',
  },
  {
    slug: 'preserves',
    name: 'Preserves',
    note: 'Whole fruit packed in thick syrup, made from the recipes Mum knows by heart.',
    image: '/images/plates/sour-cherry.jpg',
    imageAlt: 'Watercolour of four Montmorency sour cherries beside pencil-drawn leaves, painted in 1915',
  },
  {
    slug: 'fruit-butters',
    name: 'Fruit butters',
    note: 'Simmered for hours over a low fire with no added sugar, thick enough to hold a spoon upright.',
    image: '/images/plates/plum.jpg',
    imageAlt: 'Watercolour of a dusky purple plum, whole and cut in half around its stone, painted in 1935',
  },
  {
    slug: 'seasonal-editions',
    name: 'Seasonal editions',
    note: 'Small batches, made only while the fruit is in season.',
    image: '/images/plates/fig.jpg',
    imageAlt: 'Watercolour of a pale green fig, whole and cut open to its red seeds, painted in 1912',
  },
]

export function shelfHref(slug: string): string {
  return `/products?category=${slug}`
}
