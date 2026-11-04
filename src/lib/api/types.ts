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
  price_cents: number
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

export type RoleName = 'client' | 'admin'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone: string | null
  role: RoleName
}

export interface LoginDetails {
  email: string
  password: string
}

export interface RegisterDetails extends LoginDetails {
  first_name: string
  last_name: string
  phone?: string
}

export interface CartEntry {
  product_id: number
  quantity: number
}

export interface CartLine {
  product: ProductSummary
  quantity: number
  subtotal_cents: number
  is_available: boolean
}

export interface CartSummary {
  lines: CartLine[]
  missing_product_ids: number[]
  total_cents: number
}

export interface Address {
  id: number
  street: string
  city: string
  county: string
  postal_code: string
  one_line: string
}

export interface OrderStatus {
  code: string
  name: string
}

export interface OrderSummary {
  id: number
  status: OrderStatus
  created_at: string
  total_cents: number
  jar_count: number
  is_cancellable: boolean
}

export interface OrderItem {
  product_name: string
  product_slug: string
  quantity: number
  unit_price_cents: number
  subtotal_cents: number
}

export interface OrderDetail extends OrderSummary {
  items: OrderItem[]
  ships_to: string
  notes: string
}

export type QueryParams = Record<string, string | number | undefined>
