import { FormEvent, useState } from "react"
import { useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { createPerson } from "@/services/people.service"
import { onlyDigits } from "@/utils/cpf"

export function PersonCreatePage() {
  const navigate = useNavigate()
  const [fullName, setFullName] = useState("")
  const [cpf, setCpf] = useState("")
  const [email, setEmail] = useState("")
  const [error, setError] = useState("")

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    const digits = onlyDigits(cpf)
    if (digits.length !== 11) {
      setError("Informe o CPF com 11 dígitos.")
      return
    }
    setError("")
    try {
      const person = await createPerson({
        cpf: digits,
        email: email.trim(),
        full_name: fullName.trim(),
      })
      navigate(`/people/${person.id}`)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível convidar.")
    }
  }

  return (
    <form className="mx-auto max-w-lg space-y-4" onSubmit={onSubmit}>
      <h1 className="text-xl font-semibold">Convidar pessoa</h1>
      <p className="text-sm text-muted-foreground">
        A pessoa recebe um e-mail para definir a senha. A senha não é informada aqui.
      </p>
      <div className="space-y-2">
        <Label htmlFor="full_name">Nome</Label>
        <Input id="full_name" value={fullName} onChange={(event) => setFullName(event.target.value)} required />
      </div>
      <div className="space-y-2">
        <Label htmlFor="cpf">CPF</Label>
        <Input id="cpf" inputMode="numeric" value={cpf} onChange={(event) => setCpf(event.target.value)} required />
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">E-mail</Label>
        <Input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
      </div>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      <Button type="submit">Enviar convite</Button>
    </form>
  )
}
