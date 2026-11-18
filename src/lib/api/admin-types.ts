import type { CategoryRef, OrderItem, OrderStatus } from './types'

export interface AdminImage {
  id: number
  url: string
  alt_text: string
  position: number
}

export interface AdminProductSummary {
  id: number
  name: string
  slug: string
  category: CategoryRef
  price_cents: number
  weight_grams: number
  stock: number
  is_active: boolean
  image: AdminImage | null
  image_count: number
}

export interface AdminProductDetail extends AdminProductSummary {
  description: string
  ingredients: string[]
  images: AdminImage[]
  created_at: string
  can_delete: boolean
}

export interface AdminProductInput {
  name: string
  slug?: string
  category_slug: string
  description: string
  price_cents: number
  weight_grams: number
  stock: number
  ingredients: string[]
  is_active: boolean
}

export interface Customer {
  id: number
  name: string
  email: string
  phone: string | null
}

export interface AdminOrderSummary {
  id: number
  status: OrderStatus
  created_at: string
  total_cents: number
  jar_count: number
  customer: Customer
  payment_status: string | null
}

export interface AdminOrderDetail extends AdminOrderSummary {
  items: OrderItem[]
  ships_to: string
  notes: string
  paid_at: string | null
  next_statuses: OrderStatus[]
}

export interface StatusCount extends OrderStatus {
  count: number
}

export interface LowStockJar {
  id: number
  name: string
  slug: string
  stock: number
  is_active: boolean
}

export interface AdminSummary {
  revenue_cents: number
  paid_orders: number
  orders_to_send: number
  awaiting_payment: number
  messages: number
  orders_by_status: StatusCount[]
  low_stock: LowStockJar[]
  recent_orders: AdminOrderSummary[]
}

export interface ContactMessage {
  id: number
  name: string
  email: string
  subject: string
  message: string
  created_at: string
}

export interface MessagesPage {
  messages: ContactMessage[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface LogEntry {
  timestamp: string
  level: string
  ip: string
  user_id: number | null
  action: string
  details: string
}

export interface LogPage {
  entries: LogEntry[]
  total: number
  page: number
  per_page: number
  pages: number
  actions: string[]
}

export interface ContactDetails {
  name: string
  email: string
  subject: string
  message: string
}
