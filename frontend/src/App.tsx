import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom"

import { GlobalLoader } from "@/components/GlobalLoader"
import { AppShell } from "@/components/layouts/AppShell"
import { PrivateRoute } from "@/components/PrivateRoute"
import { ChangePasswordPage } from "@/pages/ChangePasswordPage"
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage"
import { LoginPage } from "@/pages/LoginPage"
import { PeoplePage } from "@/pages/PeoplePage"
import { PersonCreatePage } from "@/pages/PersonCreatePage"
import { PersonDetailPage } from "@/pages/PersonDetailPage"
import { ResetPasswordPage } from "@/pages/ResetPasswordPage"
import { VerifyEmailPage } from "@/pages/VerifyEmailPage"

const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/forgot-password", element: <ForgotPasswordPage /> },
  { path: "/reset-password", element: <ResetPasswordPage /> },
  { path: "/verify-email/confirm", element: <VerifyEmailPage /> },
  {
    element: <PrivateRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/", element: <Navigate to="/people" replace /> },
          { path: "/people", element: <PeoplePage /> },
          { path: "/people/new", element: <PersonCreatePage /> },
          { path: "/people/:id", element: <PersonDetailPage /> },
          { path: "/change-password", element: <ChangePasswordPage /> },
        ],
      },
    ],
  },
])

export function App() {
  return (
    <>
      <GlobalLoader />
      <RouterProvider router={router} />
    </>
  )
}
