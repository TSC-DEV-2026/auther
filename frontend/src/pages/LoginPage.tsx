import { FormEvent, useState } from "react"
import { Link, useNavigate } from "react-router-dom"

import { PublicFrame } from "@/components/PublicFrame"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { login } from "@/services/auth.service"
import { useAuthStore } from "@/store/auth.store"

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [message, setMessage] = useState("")

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setMessage("")
    try {
      const user = await login(email.trim(), password)
      useAuthStore.getState().setUser(user)
      useAuthStore.getState().setReady(true)
      navigate("/people")
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível entrar.")
    }
  }

  return (
    <PublicFrame title="Entrar">
      <form className="space-y-4" onSubmit={onSubmit}>
        <div className="space-y-2">
          <Label htmlFor="email">E-mail</Label>
          <Input id="email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Senha</Label>
          <Input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </div>
        {message ? <p className="text-sm text-destructive">{message}</p> : null}
        <Button type="submit" className="w-full">Entrar</Button>
        <Link to="/forgot-password" className="block text-center text-sm text-muted-foreground">
          Esqueci a senha
        </Link>
      </form>
    </PublicFrame>
  )
}
