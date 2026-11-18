import { jarLook, type Fruit } from './jars'

export type MonthSpan = readonly [first: number, last: number]

export interface HarvestRow {
  slug: string
  name: string
  fruit: Fruit
  colour: string
  spans: MonthSpan[]
}

export const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
] as const

interface HarvestEntry {
  slug: string
  name: string
  fruit: Fruit
  spans: MonthSpan[]
}

const ENTRIES: HarvestEntry[] = [
  { slug: 'orange-marmalade', name: 'Orange', fruit: 'orange', spans: [[1, 3], [12, 12]] },
  { slug: 'lemon-and-ginger-marmalade', name: 'Lemon', fruit: 'lemon', spans: [[1, 3], [12, 12]] },
  { slug: 'rose-petal-preserve', name: 'Rose petal', fruit: 'rose', spans: [[5, 6]] },
  { slug: 'strawberry-jam', name: 'Strawberry', fruit: 'strawberry', spans: [[6, 6]] },
  { slug: 'green-walnut-preserve', name: 'Green walnut', fruit: 'green-walnut', spans: [[6, 6]] },
  { slug: 'apricot-jam', name: 'Apricot', fruit: 'apricot', spans: [[7, 7]] },
  { slug: 'cherry-plum-jam', name: 'Cherry plum', fruit: 'cherry-plum', spans: [[7, 7]] },
  { slug: 'sour-cherry-preserve', name: 'Sour cherry', fruit: 'cherry', spans: [[7, 7]] },
  { slug: 'blackcurrant-jam', name: 'Blackcurrant', fruit: 'blackcurrant', spans: [[7, 7]] },
  { slug: 'peach-jam', name: 'Peach', fruit: 'peach', spans: [[7, 8]] },
  { slug: 'raspberry-jam', name: 'Raspberry', fruit: 'raspberry', spans: [[7, 8]] },
  { slug: 'wild-blueberry-jam', name: 'Blueberry', fruit: 'blueberry', spans: [[7, 8]] },
  { slug: 'forest-fruit-jam', name: 'Forest fruit', fruit: 'forest', spans: [[7, 8]] },
  { slug: 'plum-butter', name: 'Plum', fruit: 'plum', spans: [[9, 9]] },
  { slug: 'apple-butter-with-cinnamon', name: 'Apple', fruit: 'apple', spans: [[9, 10]] },
  { slug: 'pear-and-vanilla-butter', name: 'Pear', fruit: 'pear', spans: [[9, 10]] },
  { slug: 'fig-and-walnut-jam', name: 'Fig', fruit: 'fig', spans: [[9, 10]] },
  { slug: 'quince-preserve', name: 'Quince', fruit: 'quince', spans: [[10, 10]] },
  { slug: 'rosehip-jam', name: 'Rosehip', fruit: 'rosehip', spans: [[11, 11]] },
  { slug: 'lingonberry-jam', name: 'Lingonberry', fruit: 'lingonberry', spans: [[11, 11]] },
]

export function harvestRows(): HarvestRow[] {
  return ENTRIES.map((entry) => ({
    ...entry,
    colour: jarLook({ slug: entry.slug, name: entry.name }).fill,
  }))
}

export function spanLabel([first, last]: MonthSpan): string {
  const start = MONTH_NAMES[first - 1]
  return first === last ? start : `${start} to ${MONTH_NAMES[last - 1]}`
}

export function harvestLabel(row: Pick<HarvestRow, 'spans'>): string {
  return row.spans.map(spanLabel).join(' and ')
}

export function isInSeason(row: Pick<HarvestRow, 'spans'>, month: number): boolean {
  return row.spans.some(([first, last]) => month >= first && month <= last)
}
