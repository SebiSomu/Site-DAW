import type { ProductSummary } from './api/types'

export type Fruit =
  | 'apple'
  | 'apricot'
  | 'blackcurrant'
  | 'blueberry'
  | 'cherry'
  | 'fig'
  | 'green-walnut'
  | 'plum'
  | 'quince'
  | 'raspberry'
  | 'rose'
  | 'rosehip'
  | 'strawberry'

export interface JarLook {
  label: string
  fill: string
  tile: string
  fruit: Fruit | null
}

export interface JarShape {
  x: number
  y: number
  width: number
  height: number
  radius: number
  cloth: string
}

const SHAPES: Record<string, JarShape> = {
  jams: { x: 50, y: 80, width: 100, height: 100, radius: 24, cloth: '#b23a48' },
  preserves: { x: 56, y: 64, width: 88, height: 118, radius: 12, cloth: '#4f6b3a' },
  'fruit-butters': { x: 42, y: 98, width: 116, height: 84, radius: 18, cloth: '#c98a2e' },
  'seasonal-editions': { x: 52, y: 74, width: 96, height: 108, radius: 6, cloth: '#5a2a4a' },
}

const LOOKS: Record<string, JarLook> = {
  'strawberry-jam': { label: 'Strawberry', fill: '#b8222c', tile: '#f6e3df', fruit: 'strawberry' },
  'raspberry-jam': { label: 'Raspberry', fill: '#a3193f', tile: '#f6e0e6', fruit: 'raspberry' },
  'wild-blueberry-jam': { label: 'Blueberry', fill: '#33264f', tile: '#e6e3ef', fruit: 'blueberry' },
  'blackcurrant-jam': { label: 'Blackcurrant', fill: '#2a1426', tile: '#e9e0e8', fruit: 'blackcurrant' },
  'apricot-jam': { label: 'Apricot', fill: '#e08a2c', tile: '#f8ead6', fruit: 'apricot' },
  'sour-cherry-preserve': { label: 'Sour cherry', fill: '#7a1222', tile: '#f3e0e0', fruit: 'cherry' },
  'quince-preserve': { label: 'Quince', fill: '#d99a2b', tile: '#f6ecd4', fruit: 'quince' },
  'rose-petal-preserve': { label: 'Rose petal', fill: '#c9506d', tile: '#f8e4ea', fruit: 'rose' },
  'green-walnut-preserve': { label: 'Green walnut', fill: '#3a2414', tile: '#e8ecdc', fruit: 'green-walnut' },
  'plum-butter': { label: 'Plum', fill: '#3d1c2b', tile: '#ebe2e8', fruit: 'plum' },
  'apple-butter-with-cinnamon': { label: 'Apple', fill: '#8a4a22', tile: '#f3e6d8', fruit: 'apple' },
  'fig-and-walnut-jam': { label: 'Fig, walnut', fill: '#6e3a2c', tile: '#efe4dc', fruit: 'fig' },
  'rosehip-jam': { label: 'Rosehip', fill: '#c2401c', tile: '#f7e3da', fruit: 'rosehip' },
}

export function jarShape(product: Pick<ProductSummary, 'category'>): JarShape {
  return SHAPES[product.category.slug] ?? SHAPES.jams
}

export function jarLook(product: Pick<ProductSummary, 'slug' | 'name'>): JarLook {
  return LOOKS[product.slug] ?? { label: product.name, fill: '#8b2d3a', tile: '#f1e6d2', fruit: null }
}
