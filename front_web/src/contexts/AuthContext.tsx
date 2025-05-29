"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

interface User {
  id: string
  username: string
  nickname: string
  allowNotifications: boolean
  isAdmin: boolean
}

interface UpdateUserData {
  nickname?: string
  currentPassword?: string
  newPassword?: string
}

interface Notification {
  id: number
  content: string
  read: boolean
}

interface AuthContextType {
  isLoggedIn: boolean
  user: User | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  signup: (username: string, password: string, nickname: string, allowNotifications: boolean) => Promise<void>
  checkUsernameAvailability: (username: string) => Promise<boolean>
  updateUser: (data: UpdateUserData) => Promise<void>
  notifications: Notification[]
  markNotificationsAsRead: () => void
  checkNicknameAvailability: (nickname: string) => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false)
  const [user, setUser] = useState<User | null>(null)
  const [notifications, setNotifications] = useState<Notification[]>([])

  // 더미 사용자 데이터
  const dummyUsers = [
    { id: "1", username: "abc123", password: "1111", nickname: "a", allowNotifications: true, isAdmin: false },
    { id: "2", username: "ad", password: "12", nickname: "Admin", allowNotifications: false, isAdmin: true },
  ]

  useEffect(() => {
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      setUser(JSON.parse(storedUser))
      setIsLoggedIn(true)
    }

    // 더미 알림 데이터 생성
    setNotifications([
      { id: 1, content: "새로운 알림 1", read: false },
      { id: 2, content: "새로운 알림 2", read: false },
      { id: 3, content: "이전 알림", read: true },
    ])
  }, [])

  const login = async (username: string, password: string) => {
    const foundUser = dummyUsers.find((u) => u.username === username && u.password === password)
    if (foundUser) {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { password: _, ...userWithoutPassword } = foundUser
      setUser(userWithoutPassword)
      setIsLoggedIn(true)
      localStorage.setItem("user", JSON.stringify(userWithoutPassword))
    } else {
      throw new Error("Invalid credentials")
    }
  }

  const logout = () => {
    setUser(null)
    setIsLoggedIn(false)
    localStorage.removeItem("user")
  }

  const signup = async (username: string, password: string, nickname: string, allowNotifications: boolean) => {
    if (dummyUsers.some((u) => u.username === username)) {
      throw new Error("Username already exists")
    }
    const newUser = {
      id: String(dummyUsers.length + 1),
      username,
      password,
      nickname,
      allowNotifications,
      isAdmin: false,
    }
    dummyUsers.push(newUser)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password: passwordToRemove, ...userWithoutPassword } = newUser
    setUser(userWithoutPassword)
    setIsLoggedIn(true)
    localStorage.setItem("user", JSON.stringify(userWithoutPassword))
  }

  const checkUsernameAvailability = async (username: string) => {
    return !dummyUsers.some((u) => u.username === username)
  }

  const updateUser = async (data: UpdateUserData) => {
    if (!user) throw new Error("User not logged in")

    const userIndex = dummyUsers.findIndex((u) => u.id === user.id)
    if (userIndex === -1) throw new Error("User not found")

    if (data.currentPassword && data.newPassword) {
      if (dummyUsers[userIndex].password !== data.currentPassword) {
        throw new Error("Current password is incorrect")
      }
      dummyUsers[userIndex].password = data.newPassword
    }

    if (data.nickname) {
      dummyUsers[userIndex].nickname = data.nickname
      user.nickname = data.nickname
    }

    setUser({ ...user })
    localStorage.setItem("user", JSON.stringify(user))
  }

  const markNotificationsAsRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, read: true })))
  }

  const checkNicknameAvailability = async (nickname: string) => {
    return !dummyUsers.some((u) => u.nickname === nickname)
  }

  return (
    <AuthContext.Provider
      value={{
        isLoggedIn,
        user,
        login,
        logout,
        signup,
        checkUsernameAvailability,
        updateUser,
        notifications,
        markNotificationsAsRead,
        checkNicknameAvailability,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

