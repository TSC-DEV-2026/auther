export function onlyDigits(value: string): string {
  return value.replace(/\D/g, "")
}

export function formatCpf(value: string): string {
  const digits = onlyDigits(value).slice(0, 11)
  if (digits.length !== 11) {
    return digits
  }
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`
}
