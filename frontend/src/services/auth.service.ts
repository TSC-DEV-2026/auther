import { api, ensureCsrf } from "@/services/api"
import type { ApiResponse, Person } from "@/types/person"
import { apiErrorMessage } from "@/utils/api-error"

async function request<T>(work: () => Promise<{ data: ApiResponse<T> }>): Promise<T> {
  try {
    const response = await work()
    return response.data.data as T
  } catch (error) {
    throw new Error(apiErrorMessage(error))
  }
}

export function login(email: string, password: string): Promise<Person> {
  return ensureCsrf().then(() =>
    request(() => api.post<ApiResponse<Person>>("/auth/login", { email, password })),
  )
}

export function me(): Promise<Person> {
  return request(() => api.get<ApiResponse<Person>>("/auth/me"))
}

export function logout(): Promise<null> {
  return ensureCsrf().then(() => request(() => api.post<ApiResponse<null>>("/auth/logout")))
}

export function forgotPassword(email: string): Promise<{ message: string }> {
  return ensureCsrf().then(() =>
    request(() => api.post<ApiResponse<{ message: string }>>("/auth/forgot-password", { email })),
  )
}

export function resetPassword(token: string, newPassword: string): Promise<null> {
  return ensureCsrf().then(() =>
    request(() =>
      api.post<ApiResponse<null>>("/auth/reset-password", {
        token,
        new_password: newPassword,
      }),
    ),
  )
}

export function changePassword(currentPassword: string, newPassword: string): Promise<null> {
  return ensureCsrf().then(() =>
    request(() =>
      api.post<ApiResponse<null>>("/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      }),
    ),
  )
}

export function verifyEmail(token: string): Promise<null> {
  return request(() => api.get<ApiResponse<null>>("/auth/verify-email", { params: { token } }))
}

export function resendVerification(email: string): Promise<{ message: string }> {
  return ensureCsrf().then(() =>
    request(() =>
      api.post<ApiResponse<{ message: string }>>("/auth/resend-verification", { email }),
    ),
  )
}
