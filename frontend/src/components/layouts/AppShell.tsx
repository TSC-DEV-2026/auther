import { KeyRound, LogOut, Users } from "lucide-react"
import { Link, Outlet, useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { logout } from "@/services/auth.service"
import { useAuthStore } from "@/store/auth.store"

export function AppShell() {
  const user = useAuthStore((state) => state.user)
  const navigate = useNavigate()

  async function sair() {
    try {
      await logout()
    } finally {
      useAuthStore.getState().clear()
      navigate("/login")
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-3">
          <span className="font-semibold">Auther</span>
          <Link to="/people" className="inline-flex items-center gap-2 text-sm">
            <Users className="h-4 w-4" />
            Pessoas
          </Link>
          <div className="ml-auto flex items-center gap-3 text-sm">
            <span className="text-muted-foreground">{user?.email}</span>
            <Link to="/change-password" className="inline-flex items-center gap-1">
              <KeyRound className="h-4 w-4" />
              Senha
            </Link>
            <Button type="button" variant="ghost" size="sm" onClick={sair}>
              <LogOut className="h-4 w-4" />
              Sair
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
