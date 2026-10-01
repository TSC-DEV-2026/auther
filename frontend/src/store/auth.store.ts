import { create } from "zustand"

import type { Person } from "@/types/person"

type AuthState = {
  user: Person | null
  isAuthenticated: boolean
  ready: boolean
  setUser: (user: Person) => void
  clear: () => void
  setReady: (ready: boolean) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  ready: false,
  setUser: (user) => set({ user, isAuthenticated: true }),
  clear: () => set({ user: null, isAuthenticated: false }),
  setReady: (ready) => set({ ready }),
}))
