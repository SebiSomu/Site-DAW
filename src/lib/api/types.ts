export interface Category {
  id: number
  name: string
  slug: string
  description: string
}

export type CategoryRef = Pick<Category, 'name' | 'slug'>

export interface ProductImage {
  url: string
  alt_text: string
}

export interface ProductSummary {
  id: number
  name: string
  slug: string
  price_bani: number
  weight_grams: number
  stock: number
  category: CategoryRef
  image: ProductImage | null
}

export interface Review {
  id: number
  rating: number
  comment: string
  author: string
  created_at: string
}

export interface ProductDetail extends ProductSummary {
  description: string
  images: ProductImage[]
  ingredients: string[]
  average_rating: number | null
  reviews: Review[]
}

export interface ProductPage {
  items: ProductSummary[]
  total: number
  page: number
  per_page: number
  pages: number
}

export type ProductSort = 'newest' | 'price-asc' | 'price-desc' | 'name'

export type QueryParams = Record<string, string | number | undefined>
