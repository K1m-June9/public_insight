/* eslint-disable @typescript-eslint/no-unused-vars */
"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "../../contexts/AuthContext"
import Header from "../../components/Header"
import Footer from "../../components/Footer"

export default function SignupPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [nickname, setNickname] = useState("")
  const [allowNotifications, setAllowNotifications] = useState(false)
  const [error, setError] = useState("")
  const [usernameAvailable, setUsernameAvailable] = useState(false)
  const [nicknameAvailable, setNicknameAvailable] = useState(false)
  const router = useRouter()
  const { signup, checkUsernameAvailability, checkNicknameAvailability } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (password !== confirmPassword) {
      setError("비밀번호가 일치하지 않습니다.")
      return
    }

    if (!usernameAvailable) {
      setError("아이디 중복 확인을 해주세요.")
      return
    }

    if (!nicknameAvailable) {
      setError("닉네임 중복 확인을 해주세요.")
      return
    }

    try {
      await signup(username, password, nickname, allowNotifications)
      router.push("/")
    } catch (error) {
      setError("회원가입에 실패했습니다. 다시 시도해주세요.")
    }
  }

  const checkUsername = async () => {
    if (username.trim() === "") {
      setError("아이디를 입력해주세요.")
      return
    }

    try {
      const isAvailable = await checkUsernameAvailability(username)
      if (isAvailable) {
        setUsernameAvailable(true)
        setError("사용 가능한 아이디입니다.")
      } else {
        setUsernameAvailable(false)
        setError("이미 사용 중인 아이디입니다.")
      }
    } catch (error) {
      setError("아이디 확인에 실패했습니다. 다시 시도해주세요.")
    }
  }

  const checkNickname = async () => {
    if (nickname.trim() === "") {
      setError("닉네임을 입력해주세요.")
      return
    }

    try {
      const isAvailable = await checkNicknameAvailability(nickname)
      if (isAvailable) {
        setNicknameAvailable(true)
        setError("사용 가능한 닉네임입니다.")
      } else {
        setNicknameAvailable(false)
        setError("이미 사용 중인 닉네임입니다.")
      }
    } catch (error) {
      setError("닉네임 확인에 실패했습니다. 다시 시도해주세요.")
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">회원가입</h2>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="rounded-md shadow-sm -space-y-px">
              <div className="relative">
                <div className="flex items-center">
                  <div className="flex-grow">
                    <label htmlFor="username" className="sr-only">
                      아이디
                    </label>
                    <input
                      id="username"
                      name="username"
                      type="text"
                      required
                      className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm pr-24"
                      placeholder="아이디"
                      value={username}
                      onChange={(e) => {
                        setUsername(e.target.value)
                        setUsernameAvailable(false)
                      }}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={checkUsername}
                    className="absolute right-0 top-0 h-full px-4 py-2 border border-transparent text-sm font-medium rounded-tr-md text-white bg-sky-300 hover:bg-sky-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500"
                  >
                    중복 확인
                  </button>
                </div>
              </div>
              <div>
                <label htmlFor="password" className="sr-only">
                  비밀번호
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="비밀번호"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="confirm-password" className="sr-only">
                  비밀번호 확인
                </label>
                <input
                  id="confirm-password"
                  name="confirm-password"
                  type="password"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="비밀번호 확인"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
              <div className="relative">
                <div className="flex items-center">
                  <div className="flex-grow">
                    <label htmlFor="nickname" className="sr-only">
                      닉네임
                    </label>
                    <input
                      id="nickname"
                      name="nickname"
                      type="text"
                      required
                      className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm pr-24"
                      placeholder="닉네임"
                      value={nickname}
                      onChange={(e) => {
                        setNickname(e.target.value)
                        setNicknameAvailable(false)
                      }}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={checkNickname}
                    className="absolute right-0 top-0 h-full px-4 py-2 border border-transparent text-sm font-medium rounded-tr-md text-white bg-sky-300 hover:bg-sky-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500"
                  >
                    중복 확인
                  </button>
                </div>
              </div>
            </div>

            <div className="flex items-center">
              <input
                id="allow-notifications"
                name="allow-notifications"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                checked={allowNotifications}
                onChange={(e) => setAllowNotifications(e.target.checked)}
              />
              <label htmlFor="allow-notifications" className="ml-2 block text-sm text-gray-900">
                알림 허용
              </label>
            </div>

            {error && (
              <div className={`text-sm mt-2 ${error.includes("사용 가능") ? "text-green-500" : "text-red-500"}`}>
                {error}
              </div>
            )}

            <div>
              <button
                type="submit"
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                회원가입
              </button>
            </div>
          </form>
          <div className="text-sm text-center">
            <Link href="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
              이미 계정이 있으신가요? 로그인
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}

