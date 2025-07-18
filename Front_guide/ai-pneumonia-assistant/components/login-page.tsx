"use client"

import type React from "react"

import { useState } from "react"
import { Eye, EyeOff, Stethoscope, User, Lock, AlertCircle, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { useAuth } from "@/lib/auth-context"

export default function LoginPage() {
  const { login } = useAuth()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const demoUsers = [
    { username: "User", password: "user_prueba123", role: "médico", name: "User" },]

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const user = demoUsers.find((u) => u.username === username && u.password === password)

    if (user) {
      login({
        id: user.username,
        name: user.name,
        username: user.username,
        role: user.role.toLowerCase() as "administrador" | "médico" | "radiólogo" | "viewer",
      })
    } else {
      setError("Credenciales incorrectas. Verifique su usuario y contraseña.")
    }

    setIsLoading(false)
  }

  const handleDemoLogin = (demoUser: (typeof demoUsers)[0]) => {
    setUsername(demoUser.username)
    setPassword(demoUser.password)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left Side - Branding */}
        <div className="text-center lg:text-left">
          <div className="flex items-center justify-center lg:justify-start gap-3 mb-6">
            <Stethoscope className="h-12 w-12 text-blue-600" />
            <div>
              <h1 className="text-4xl font-bold text-gray-900">RADOX</h1>
              <h2 className="text-2xl font-semibold text-blue-600">Assistant</h2>
            </div>
          </div>
          <p className="text-xl text-gray-600 mb-8">
            Sistema inteligente para la detección y análisis de neumonía mediante inteligencia artificial
          </p>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Análisis IA Avanzado</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Reportes Automáticos</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Gestión de Pacientes</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Interfaz Intuitiva</span>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <Card className="w-full max-w-md mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Iniciar Sesión</CardTitle>
            <p className="text-gray-600">Acceda al sistema con sus credenciales</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <Label htmlFor="username">Usuario</Label>
                <div className="relative mt-1">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Ingrese su usuario"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="password">Contraseña</Label>
                <div className="relative mt-1">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Ingrese su contraseña"
                    className="pl-10 pr-10"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 p-3 rounded-md">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
              )}

              <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
                {isLoading ? "Iniciando sesión..." : "Iniciar Sesión"}
              </Button>
            </form>

            {/* Demo Users */}
            <div className="mt-6 pt-6 border-t">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Usuarios de Demostración:</h3>
              <div className="grid grid-cols-1 gap-2">
                {demoUsers.map((user) => (
                  <Button
                    key={user.username}
                    variant="outline"
                    size="sm"
                    onClick={() => handleDemoLogin(user)}
                    className="justify-between text-left h-auto p-3"
                  >
                    <div>
                      <div className="font-medium">{user.name}</div>
                      <div className="text-xs text-gray-500">@{user.username}</div>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {user.role}
                    </Badge>
                  </Button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-3 text-center">
                Haga clic en cualquier usuario para autocompletar las credenciales
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
        <p className="text-xs text-gray-500 text-center">
          Sistema de Demostración • Todos los datos son ficticios • v1.0.0
        </p>
      </div>
    </div>
  )
}
