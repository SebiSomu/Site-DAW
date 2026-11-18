import type { ProductSummary } from './api/types'

export type Fruit =
  | 'apple'
  | 'apricot'
  | 'blackcurrant'
  | 'blueberry'
  | 'cherry'
  | 'cherry-plum'
  | 'fig'
  | 'forest'
  | 'green-walnut'
  | 'lemon'
  | 'lingonberry'
  | 'orange'
  | 'peach'
  | 'pear'
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

export interface JarPhoto {
  src: string
  srcset: string
  alt: string
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
  'peach-jam': { label: 'Peach', fill: '#e9983f', tile: '#f9e7d8', fruit: 'peach' },
  'cherry-plum-jam': { label: 'Cherry plum', fill: '#c8483a', tile: '#f8e6d6', fruit: 'cherry-plum' },
  'forest-fruit-jam': { label: 'Forest fruit', fill: '#4a1830', tile: '#ece0e6', fruit: 'forest' },
  'pear-and-vanilla-butter': { label: 'Pear, vanilla', fill: '#cfae7a', tile: '#f4ecd9', fruit: 'pear' },
  'lingonberry-jam': { label: 'Lingonberry', fill: '#a3182f', tile: '#f4e0e0', fruit: 'lingonberry' },
  'orange-marmalade': { label: 'Orange', fill: '#c9631a', tile: '#f9e5cf', fruit: 'orange' },
  'lemon-and-ginger-marmalade': { label: 'Lemon, ginger', fill: '#e6bf4a', tile: '#f8f0cf', fruit: 'lemon' },
  'rosehip-jam': { label: 'Rosehip', fill: '#c2401c', tile: '#f7e3da', fruit: 'rosehip' },
}

const PHOTOS: Record<string, JarPhoto> = {
  'apricot-jam': {
    src: '/images/jars/apricot.webp',
    srcset: '/images/jars/apricot-512.webp 512w, /images/jars/apricot.webp 1024w',
    alt: 'Illustrative photo of a round jar of apricot jam with a red gingham lid tied with twine, beside fresh apricots, a halved apricot and a slice of lemon',
  },
  'strawberry-jam': {
    src: '/images/jars/strawberry.webp',
    srcset: '/images/jars/strawberry-512.webp 512w, /images/jars/strawberry.webp 1024w',
    alt: 'Illustrative photo of a round jar of strawberry jam with a red gingham lid tied with twine, beside ripe strawberries, a halved strawberry and white flowers',
  },
  'raspberry-jam': {
    src: '/images/jars/raspberry.webp',
    srcset: '/images/jars/raspberry-512.webp 512w, /images/jars/raspberry.webp 1024w',
    alt: 'Illustrative photo of a round jar of raspberry jam with a red gingham lid tied with twine, beside fresh raspberries and a leafy cane',
  },
  'wild-blueberry-jam': {
    src: '/images/jars/wild-blueberry.webp',
    srcset: '/images/jars/wild-blueberry-512.webp 512w, /images/jars/wild-blueberry.webp 1024w',
    alt: 'Illustrative photo of a round jar of wild blueberry jam with a red gingham lid tied with twine, beside wild blueberries on a leafy sprig and a little moss',
  },
  'blackcurrant-jam': {
    src: '/images/jars/blackcurrant.webp',
    srcset: '/images/jars/blackcurrant-512.webp 512w, /images/jars/blackcurrant.webp 1024w',
    alt: 'Illustrative photo of a round jar of blackcurrant jam with a red gingham lid tied with twine, beside black currants on their stems, a leaf and a piece of hard cheese',
  },
  'sour-cherry-preserve': {
    src: '/images/jars/sour-cherry.webp',
    srcset: '/images/jars/sour-cherry-512.webp 512w, /images/jars/sour-cherry.webp 1024w',
    alt: 'Illustrative photo of a tall jar of sour cherry preserve with an olive gingham lid tied with twine, beside fresh cherries, a cherry pitter and a glass of water with a spoon',
  },
  'quince-preserve': {
    src: '/images/jars/quince.webp',
    srcset: '/images/jars/quince-512.webp 512w, /images/jars/quince.webp 1024w',
    alt: 'Illustrative photo of a tall jar of quince preserve in thick golden syrup with an olive gingham lid tied with twine, beside a whole quince, vanilla pods and a curl of lemon zest',
  },
  'rose-petal-preserve': {
    src: '/images/jars/rose-petal.webp',
    srcset: '/images/jars/rose-petal-512.webp 512w, /images/jars/rose-petal.webp 1024w',
    alt: 'Illustrative photo of a tall jar of rose petal preserve with an olive gingham lid tied with twine, beside fresh pink roses and loose petals',
  },
  'green-walnut-preserve': {
    src: '/images/jars/green-walnut.webp',
    srcset: '/images/jars/green-walnut-512.webp 512w, /images/jars/green-walnut.webp 1024w',
    alt: 'Illustrative photo of a tall jar of green walnut preserve in dark amber syrup with an olive gingham lid tied with twine, beside young green walnuts, one cut open, and a leaf',
  },
  'plum-butter': {
    src: '/images/jars/plum-butter.webp',
    srcset: '/images/jars/plum-butter-512.webp 512w, /images/jars/plum-butter.webp 1024w',
    alt: 'Illustrative photo of a wide jar of plum butter with a mustard gingham lid tied with twine, beside ripe plums, one halved, and a copper pot',
  },
  'apple-butter-with-cinnamon': {
    src: '/images/jars/apple-butter.webp',
    srcset: '/images/jars/apple-butter-512.webp 512w, /images/jars/apple-butter.webp 1024w',
    alt: 'Illustrative photo of a wide jar of apple butter with cinnamon and a mustard gingham lid tied with twine, beside apples, an apple slice and cinnamon sticks',
  },
  'fig-and-walnut-jam': {
    src: '/images/jars/fig-walnut.webp',
    srcset: '/images/jars/fig-walnut-512.webp 512w, /images/jars/fig-walnut.webp 1024w',
    alt: 'Illustrative photo of a hexagonal jar of fig and walnut jam with a plum gingham lid tied with twine, beside ripe figs, one cut open, and walnuts',
  },
  'rosehip-jam': {
    src: '/images/jars/rosehip.webp',
    srcset: '/images/jars/rosehip-512.webp 512w, /images/jars/rosehip.webp 1024w',
    alt: 'Illustrative photo of a hexagonal jar of rosehip jam with a plum gingham lid tied with twine, beside a thorny branch of frosted rosehips',
  },
  'peach-jam': {
    src: '/images/jars/peach.webp',
    srcset: '/images/jars/peach-512.webp 512w, /images/jars/peach.webp 1024w',
    alt: 'Illustrative photo of a round jar of peach jam with thick peach slices and a red gingham lid tied with twine, beside two fresh peaches, a halved peach and leaves',
  },
  'cherry-plum-jam': {
    src: '/images/jars/cherry-plum.webp',
    srcset: '/images/jars/cherry-plum-512.webp 512w, /images/jars/cherry-plum.webp 1024w',
    alt: 'Illustrative photo of a round jar of cherry plum jam with whole golden-red plums and a red gingham lid tied with twine, beside fresh cherry plums on their stems, one halved, and two leaves',
  },
  'forest-fruit-jam': {
    src: '/images/jars/forest-fruit.webp',
    srcset: '/images/jars/forest-fruit-512.webp 512w, /images/jars/forest-fruit.webp 1024w',
    alt: 'Illustrative photo of a round jar of deep crimson forest fruit jam with a red gingham lid tied with twine, beside blackberries, raspberries, blueberries and wild strawberries',
  },
  'pear-and-vanilla-butter': {
    src: '/images/jars/pear-vanilla.webp',
    srcset: '/images/jars/pear-vanilla-512.webp 512w, /images/jars/pear-vanilla.webp 1024w',
    alt: 'Illustrative photo of a wide jar of smooth pear and vanilla butter with a mustard gingham lid tied with twine, beside ripe pears, one halved, and two vanilla pods',
  },
  'lingonberry-jam': {
    src: '/images/jars/lingonberry.webp',
    srcset: '/images/jars/lingonberry-512.webp 512w, /images/jars/lingonberry.webp 1024w',
    alt: 'Illustrative photo of a hexagonal jar of lingonberry jam full of whole ruby berries with a plum gingham lid tied with twine, beside a sprig of lingonberries, loose berries and moss',
  },
  'orange-marmalade': {
    src: '/images/jars/orange-marmalade.webp',
    srcset: '/images/jars/orange-marmalade-512.webp 512w, /images/jars/orange-marmalade.webp 1024w',
    alt: 'Illustrative photo of a hexagonal jar of amber orange marmalade with fine peel shreds and a plum gingham lid tied with twine, beside whole and halved oranges and curls of peel',
  },
  'lemon-and-ginger-marmalade': {
    src: '/images/jars/lemon-ginger.webp',
    srcset: '/images/jars/lemon-ginger-512.webp 512w, /images/jars/lemon-ginger.webp 1024w',
    alt: 'Illustrative photo of a hexagonal jar of pale golden lemon and ginger marmalade with a plum gingham lid tied with twine, beside a halved lemon, a knob of ginger and a curl of peel',
  },
}

export function jarPhoto(product: Pick<ProductSummary, 'slug'>): JarPhoto | null {
  return PHOTOS[product.slug] ?? null
}

export function jarShape(product: Pick<ProductSummary, 'category'>): JarShape {
  return SHAPES[product.category.slug] ?? SHAPES.jams
}

export function jarLook(product: Pick<ProductSummary, 'slug' | 'name'>): JarLook {
  return LOOKS[product.slug] ?? { label: product.name, fill: '#8b2d3a', tile: '#f1e6d2', fruit: null }
}
