export type Person = {
  id: number
  cpf: string
  email: string
  full_name: string
  email_verified: boolean
  is_active: boolean
  is_platform_admin: boolean
}

export type PersonPage = {
  items: Person[]
  total: number
  page: number
  limit: number
}

export type ApiResponse<T> = {
  data: T | null
  error: { message: string } | null
}
