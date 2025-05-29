"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import MyPage from "@/components/MyPage"
import Header from "@/components/Header"
import Footer from "@/components/Footer"
import { useAuth } from "@/contexts/AuthContext"

export default function MyPageRoute() {
  const { isLoggedIn } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoggedIn) {
      router.push("/login")
    }
  }, [isLoggedIn, router])

  if (!isLoggedIn) {
    return null // 로그인 체크 중에는 아무것도 렌더링하지 않음
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow">
        <MyPage />
      </main>
      <Footer />
    </div>
  )
}

