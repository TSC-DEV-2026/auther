import { FormEvent, useEffect, useState } from "react"
import { useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { getPerson, updatePerson } from "@/services/people.service"
import type { Person } from "@/types/person"
import { onlyDigits } from "@/utils/cpf"

export function PersonDetailPage() {
  const params = useParams()
  const personId = Number(params.id)
  const [person, setPerson] = useState<Person | null>(null)
  const [fullName, setFullName] = useState("")
  const [cpf, setCpf] = useState("")
  const [email, setEmail] = useState("")
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  useEffect(() => {
    if (!Number.isInteger(personId)) {
      setError("Pessoa inválida.")
      return
    }
    getPerson(personId)
      .then((found) => {
        setPerson(found)
        setFullName(found.full_name)
        setCpf(found.cpf)
        setEmail(found.email)
      })
      .catch((caught: unknown) => {
        setError(caught instanceof Error ? caught.message : "Não foi possível abrir o cadastro.")
      })
  }, [personId])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    const digits = onlyDigits(cpf)
    if (digits.length !== 11) {
      setError("Informe o CPF com 11 dígitos.")
      return
    }
    setError("")
    setMessage("")
    try {
      const updated = await updatePerson(personId, {
        cpf: digits,
        email: email.trim(),
        full_name: fullName.trim(),
      })
      setPerson(updated)
      setMessage("Cadastro atualizado.")
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível salvar.")
    }
  }

  async function toggleActive() {
    if (!person) {
      return
    }
    setError("")
    setMessage("")
    try {
      const updated = await updatePerson(personId, { is_active: !person.is_active })
      setPerson(updated)
      setMessage(updated.is_active ? "Pessoa ativada." : "Pessoa desativada.")
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível alterar a situação.")
    }
  }

  if (!person && !error) {
    return null
  }

  return (
    <form className="mx-auto max-w-lg space-y-4" onSubmit={onSubmit}>
      <h1 className="text-xl font-semibold">Cadastro</h1>
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
      {person ? (
        <p className="text-sm text-muted-foreground">
          {person.is_active ? "Ativa" : "Inativa"}
          {person.email_verified ? " · e-mail verificado" : " · e-mail não verificado"}
          {person.is_platform_admin ? " · admin da plataforma" : ""}
        </p>
      ) : null}
      {message ? <p className="text-sm">{message}</p> : null}
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      <div className="flex gap-2">
        <Button type="submit">Salvar</Button>
        {person ? (
          <Button type="button" variant={person.is_active ? "destructive" : "outline"} onClick={toggleActive}>
            {person.is_active ? "Desativar" : "Ativar"}
          </Button>
        ) : null}
      </div>
    </form>
  )
}
