import type { CategoryRef } from './api/types'

export interface SeasonJar {
  slug: string
  name: string
  category: CategoryRef
}

export interface Season {
  id: string
  months: string
  title: string
  story: string
  jars: SeasonJar[]
}

const JAMS: CategoryRef = { slug: 'jams', name: 'Jams' }
const PRESERVES: CategoryRef = { slug: 'preserves', name: 'Preserves' }
const BUTTERS: CategoryRef = { slug: 'fruit-butters', name: 'Fruit butters' }
const SEASONAL: CategoryRef = { slug: 'seasonal-editions', name: 'Seasonal editions' }

export const SEASONS: Season[] = [
  {
    id: 'late-spring',
    months: 'May and June',
    title: 'Roses before breakfast',
    story:
      'The year starts at dawn, picking rose petals before the sun gets to them. Then come the first strawberries, and the young green walnuts that have to soak for days before they go anywhere near the pot.',
    jars: [
      { slug: 'rose-petal-preserve', name: 'Rose Petal Preserve', category: PRESERVES },
      { slug: 'strawberry-jam', name: 'Strawberry Jam', category: JAMS },
      { slug: 'green-walnut-preserve', name: 'Green Walnut Preserve', category: PRESERVES },
    ],
  },
  {
    id: 'high-summer',
    months: 'July and August',
    title: 'Red fingers, full kitchen',
    story:
      'The busy weeks. Apricots come in from the family orchard, berries come down from the mountains around Brașov, and anyone who walks into the kitchen is handed a bowl of sour cherries and a pitter.',
    jars: [
      { slug: 'apricot-jam', name: 'Apricot Jam', category: JAMS },
      { slug: 'sour-cherry-preserve', name: 'Sour Cherry Preserve', category: PRESERVES },
      { slug: 'raspberry-jam', name: 'Raspberry Jam', category: JAMS },
      { slug: 'wild-blueberry-jam', name: 'Wild Blueberry Jam', category: JAMS },
      { slug: 'blackcurrant-jam', name: 'Blackcurrant Jam', category: JAMS },
    ],
  },
  {
    id: 'autumn',
    months: 'September and October',
    title: 'The long simmer',
    story:
      'Plum butter day is a whole day: the copper cauldron, a wooden paddle and no sugar at all, just plums cooked until they turn almost black. Jonathan apples, quinces and the few figs we get follow close behind.',
    jars: [
      { slug: 'plum-butter', name: 'Plum Butter', category: BUTTERS },
      { slug: 'apple-butter-with-cinnamon', name: 'Apple Butter with Cinnamon', category: BUTTERS },
      { slug: 'quince-preserve', name: 'Quince Preserve', category: PRESERVES },
      { slug: 'fig-and-walnut-jam', name: 'Fig and Walnut Jam', category: SEASONAL },
    ],
  },
  {
    id: 'first-frost',
    months: 'November',
    title: 'After the first frost',
    story:
      'Rosehips taste best once the frost has touched them. They are cleaned one by one at the kitchen table, with the radio on, which is the only way anyone has found to make it bearable.',
    jars: [{ slug: 'rosehip-jam', name: 'Rosehip Jam', category: SEASONAL }],
  },
  {
    id: 'winter',
    months: 'December to April',
    title: 'The pantry rests',
    story:
      'No fruit, no fire. Winter is for writing labels, cutting gingham for the lids, reading the old notebook again and deciding which recipe gets another go next year.',
    jars: [],
  },
]

export function productHref(slug: string): string {
  return `/products/${slug}`
}
