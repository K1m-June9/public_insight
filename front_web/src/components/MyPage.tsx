/* eslint-disable @typescript-eslint/no-unused-vars */
"use client"

import type React from "react"

import { useState, useCallback } from "react"
import Link from "next/link"
import { useAuth } from "../contexts/AuthContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Bell, Bookmark } from "lucide-react"
import { useSearchParams } from "next/navigation"

export default function MyPage() {
  const searchParams = useSearchParams()
  const defaultTab = searchParams?.get("tab") || "profile"
  const { user, updateUser, notifications, checkNicknameAvailability } = useAuth()
  const [nickname, setNickname] = useState(user?.nickname || "")
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmNewPassword, setConfirmNewPassword] = useState("")
  const [error, setError] = useState("")
  const [bookmarkedFeeds, setBookmarkedFeeds] = useState([
    { id: 1, title: "북마크된 피드 1" },
    { id: 2, title: "북마크된 피드 2" },
    { id: 3, title: "북마크된 피드 3" },
  ])
  const [isNicknameAvailable, setIsNicknameAvailable] = useState(true)

  const handleCheckNickname = useCallback(async () => {
    if (nickname.trim() === "") {
      setError("닉네임을 입력해주세요.")
      return
    }
    try {
      const isAvailable = await checkNicknameAvailability(nickname)
      setIsNicknameAvailable(isAvailable)
      setError(isAvailable ? "사용 가능한 닉네임입니다." : "이미 사용 중인 닉네임입니다.")
    } catch (error) {
      setError("닉네임 확인에 실패했습니다. 다시 시도해주세요.")
    }
  }, [nickname, checkNicknameAvailability])

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (newPassword !== confirmNewPassword) {
      setError("새 비밀번호가 일치하지 않습니다.")
      return
    }

    if (!isNicknameAvailable) {
      setError("닉네임 중복 확인을 해주세요.")
      return
    }

    try {
      await updateUser({ nickname, currentPassword, newPassword })
      setCurrentPassword("")
      setNewPassword("")
      setConfirmNewPassword("")
      alert("프로필이 업데이트되었습니다.")
    } catch (error) {
      setError("프로필 업데이트에 실패했습니다. 다시 시도해주세요.")
    }
  }

  const handleRemoveBookmark = (id: number) => {
    setBookmarkedFeeds(bookmarkedFeeds.filter((feed) => feed.id !== id))
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">마이페이지</h1>
      <Tabs defaultValue={defaultTab}>
        <TabsList>
          <TabsTrigger value="profile">회원정보 수정</TabsTrigger>
          <TabsTrigger value="bookmarks">북마크</TabsTrigger>
          <TabsTrigger value="notifications">알림</TabsTrigger>
        </TabsList>
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>회원정보 수정</CardTitle>
              <CardDescription>닉네임과 비밀번호를 변경할 수 있습니다.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile}>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="username">아이디</Label>
                    <Input id="username" value={user?.username} disabled />
                  </div>
                  <div className="relative">
                    <Label htmlFor="nickname">닉네임</Label>
                    <div className="flex items-center">
                      <Input
                        id="nickname"
                        value={nickname}
                        onChange={(e) => {
                          setNickname(e.target.value)
                          setIsNicknameAvailable(false)
                        }}
                        className="pr-20"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        className="absolute right-0"
                        onClick={handleCheckNickname}
                      >
                        중복 확인
                      </Button>
                    </div>
                    {error && (
                      <p className={`text-sm mt-1 ${error.includes("사용 가능") ? "text-blue-500" : "text-red-500"}`}>
                        {error}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="currentPassword">현재 비밀번호</Label>
                    <Input
                      id="currentPassword"
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="newPassword">새 비밀번호</Label>
                    <Input
                      id="newPassword"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="confirmNewPassword">새 비밀번호 확인</Label>
                    <Input
                      id="confirmNewPassword"
                      type="password"
                      value={confirmNewPassword}
                      onChange={(e) => setConfirmNewPassword(e.target.value)}
                    />
                  </div>
                </div>
                <CardFooter className="flex justify-end mt-4 p-0">
                  <Button type="submit">저장</Button>
                </CardFooter>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="bookmarks">
          <Card>
            <CardHeader>
              <CardTitle>북마크</CardTitle>
              <CardDescription>북마크한 피드 목록입니다.</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 divide-y divide-gray-200">
                {bookmarkedFeeds.map((feed) => (
                  <li key={feed.id} className="flex items-center space-x-2 py-2">
                    <Bookmark
                      className="w-4 h-4 text-blue-500 cursor-pointer"
                      onClick={() => handleRemoveBookmark(feed.id)}
                    />
                    <Link href={`/feed/${feed.id}`} className="hover:underline">
                      <span>{feed.title}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>알림</CardTitle>
              <CardDescription>최근 알림 목록입니다.</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 divide-y divide-gray-200">
                {notifications.map((notification) => (
                  <li key={notification.id} className="flex items-center space-x-2 py-2">
                    <Bell className={`w-4 h-4 ${notification.read ? "text-gray-400" : "text-blue-500"}`} />
                    <span>{notification.content}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

