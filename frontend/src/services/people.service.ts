import { api, ensureCsrf } from "@/services/api"
import type { ApiResponse, Person, PersonPage } from "@/types/person"
import { apiErrorMessage } from "@/utils/api-error"

async function request<T>(work: () => Promise<{ data: ApiResponse<T> }>): Promise<T> {
  try {
    const response = await work()
    return response.data.data as T
  } catch (error) {
    throw new Error(apiErrorMessage(error))
  }
}

export function listPeople(params: {
  page: number
  limit: number
  cpf?: string
  email?: string
}): Promise<PersonPage> {
  return request(() => api.get<ApiResponse<PersonPage>>("/people", { params }))
}

export function getPerson(id: number): Promise<Person> {
  return request(() => api.get<ApiResponse<Person>>(`/people/${id}`))
}

export function createPerson(body: {
  cpf: string
  email: string
  full_name: string
}): Promise<Person> {
  return ensureCsrf().then(() => request(() => api.post<ApiResponse<Person>>("/people", body)))
}

export function updatePerson(
  id: number,
  body: { cpf?: string; email?: string; full_name?: string; is_active?: boolean },
): Promise<Person> {
  return ensureCsrf().then(() =>
    request(() => api.put<ApiResponse<Person>>(`/people/${id}`, body)),
  )
}

export function removePerson(id: number): Promise<null> {
  return ensureCsrf().then(() => request(() => api.delete<ApiResponse<null>>(`/people/${id}`)))
}
