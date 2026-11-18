import type { CategoryRef } from './api/types'

export interface SeasonJar {
  slug: string
  name: string
  category: CategoryRef
}

export interface Season {
  id: string
  months: string
  shortMonths: string
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
    shortMonths: 'May – Jun',
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
    shortMonths: 'Jul – Aug',
    title: 'Red fingers, full kitchen',
    story:
      'The busy weeks. Apricots and peaches come in from the family orchard, berries come down from the mountains around Brașov, and anyone who walks into the kitchen is handed a bowl of sour cherries and a pitter.',
    jars: [
      { slug: 'apricot-jam', name: 'Apricot Jam', category: JAMS },
      { slug: 'sour-cherry-preserve', name: 'Sour Cherry Preserve', category: PRESERVES },
      { slug: 'peach-jam', name: 'Peach Jam', category: JAMS },
      { slug: 'cherry-plum-jam', name: 'Cherry Plum Jam', category: JAMS },
      { slug: 'raspberry-jam', name: 'Raspberry Jam', category: JAMS },
      { slug: 'wild-blueberry-jam', name: 'Wild Blueberry Jam', category: JAMS },
      { slug: 'forest-fruit-jam', name: 'Forest Fruit Jam', category: JAMS },
      { slug: 'blackcurrant-jam', name: 'Blackcurrant Jam', category: JAMS },
    ],
  },
  {
    id: 'autumn',
    months: 'September and October',
    shortMonths: 'Sep – Oct',
    title: 'The long simmer',
    story:
      'Plum butter day is a whole day: the copper cauldron, a wooden paddle and no sugar at all, just plums cooked until they turn almost black. Jonathan apples, pears, quinces and the few figs we get follow close behind.',
    jars: [
      { slug: 'plum-butter', name: 'Plum Butter', category: BUTTERS },
      { slug: 'pear-and-vanilla-butter', name: 'Pear and Vanilla Butter', category: BUTTERS },
      { slug: 'apple-butter-with-cinnamon', name: 'Apple Butter with Cinnamon', category: BUTTERS },
      { slug: 'quince-preserve', name: 'Quince Preserve', category: PRESERVES },
      { slug: 'fig-and-walnut-jam', name: 'Fig and Walnut Jam', category: SEASONAL },
    ],
  },
  {
    id: 'first-frost',
    months: 'November',
    shortMonths: 'Nov',
    title: 'After the first frost',
    story:
      'Rosehips taste best once the frost has touched them. They are cleaned one by one at the kitchen table, with the radio on, which is the only way anyone has found to make it bearable. The last lingonberries come down from the mountain the same week.',
    jars: [
      { slug: 'rosehip-jam', name: 'Rosehip Jam', category: SEASONAL },
      { slug: 'lingonberry-jam', name: 'Lingonberry Jam', category: SEASONAL },
    ],
  },
  {
    id: 'winter',
    months: 'December to March',
    shortMonths: 'Dec – Mar',
    title: 'Marmalade weather',
    story:
      'When the orchard is bare, the oranges and lemons arrive. Peel gets sliced as thin as thread, the kitchen windows steam up, and the labels get written in the evenings while the marmalade sets.',
    jars: [
      { slug: 'orange-marmalade', name: 'Orange Marmalade', category: SEASONAL },
      { slug: 'lemon-and-ginger-marmalade', name: 'Lemon and Ginger Marmalade', category: SEASONAL },
    ],
  },
]

export function productHref(slug: string): string {
  return `/products/${slug}`
}
