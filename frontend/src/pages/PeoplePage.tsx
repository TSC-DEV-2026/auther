import { FormEvent, useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { listPeople } from "@/services/people.service"
import type { Person } from "@/types/person"
import { formatCpf, onlyDigits } from "@/utils/cpf"

export function PeoplePage() {
  const [cpf, setCpf] = useState("")
  const [email, setEmail] = useState("")
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [items, setItems] = useState<Person[]>([])
  const [error, setError] = useState("")
  const limit = 10

  async function load(nextPage: number, filters: { cpf: string; email: string }) {
    const digits = onlyDigits(filters.cpf)
    if (digits && digits.length !== 11) {
      setError("Informe o CPF com 11 dígitos.")
      setItems([])
      setTotal(0)
      return
    }
    setError("")
    const result = await listPeople({
      page: nextPage,
      limit,
      cpf: digits || undefined,
      email: filters.email.trim() || undefined,
    })
    setItems(result.items)
    setTotal(result.total)
    setPage(result.page)
  }

  useEffect(() => {
    load(1, { cpf: "", email: "" }).catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "Não foi possível listar.")
    })
  }, [])

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    load(1, { cpf, email }).catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "Não foi possível buscar.")
    })
  }

  function goTo(nextPage: number) {
    load(nextPage, { cpf, email }).catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "Não foi possível listar.")
    })
  }

  const pages = Math.max(1, Math.ceil(total / limit))

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Pessoas</h1>
        <Button asChild>
          <Link to="/people/new">Convidar</Link>
        </Button>
      </div>
      <form className="grid gap-3 sm:grid-cols-[1fr_1fr_auto]" onSubmit={onSubmit}>
        <div className="space-y-2">
          <Label htmlFor="cpf">CPF</Label>
          <Input id="cpf" inputMode="numeric" value={cpf} onChange={(event) => setCpf(event.target.value)} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">E-mail</Label>
          <Input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </div>
        <div className="flex items-end">
          <Button type="submit">Buscar</Button>
        </div>
      </form>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      {items.length === 0 && !error ? (
        <p className="text-sm text-muted-foreground">Nenhuma pessoa encontrada.</p>
      ) : null}
      {items.length > 0 ? (
        <div className="overflow-hidden rounded-lg border border-border bg-card">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted text-muted-foreground">
              <tr>
                <th className="px-4 py-2 font-medium">Nome</th>
                <th className="px-4 py-2 font-medium">CPF</th>
                <th className="px-4 py-2 font-medium">E-mail</th>
                <th className="px-4 py-2 font-medium">Situação</th>
              </tr>
            </thead>
            <tbody>
              {items.map((person) => (
                <tr key={person.id} className="border-t border-border">
                  <td className="px-4 py-2">
                    <Link to={`/people/${person.id}`} className="font-medium">
                      {person.full_name}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{formatCpf(person.cpf)}</td>
                  <td className="px-4 py-2">{person.email}</td>
                  <td className="px-4 py-2">{person.is_active ? "Ativa" : "Inativa"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">
          {total} {total === 1 ? "pessoa" : "pessoas"}
        </span>
        <div className="flex gap-2">
          <Button type="button" variant="outline" size="sm" disabled={page <= 1} onClick={() => goTo(page - 1)}>
            Anterior
          </Button>
          <span className="self-center">
            {page} / {pages}
          </span>
          <Button type="button" variant="outline" size="sm" disabled={page >= pages} onClick={() => goTo(page + 1)}>
            Próxima
          </Button>
        </div>
      </div>
    </div>
  )
}
