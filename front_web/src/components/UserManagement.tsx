"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

type User = {
  id: string
  username: string
  isBanned: boolean
  banExpiration: string | null
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([
    { id: "1", username: "user1", isBanned: false, banExpiration: null },
    { id: "2", username: "user2", isBanned: true, banExpiration: "2023-12-31" },
    { id: "3", username: "user3", isBanned: false, banExpiration: null },
  ])

  const [selectedUser, setSelectedUser] = useState<string>("")
  const [banDuration, setBanDuration] = useState<string>("7days")

  const handleBanUser = () => {
    if (!selectedUser) return

    setUsers((prevUsers) =>
      prevUsers.map((user) => {
        if (user.id === selectedUser) {
          const today = new Date()
          let expirationDate: Date | null = null

          switch (banDuration) {
            case "7days":
              expirationDate = new Date(today.setDate(today.getDate() + 7))
              break
            case "30days":
              expirationDate = new Date(today.setDate(today.getDate() + 30))
              break
            case "permanent":
              expirationDate = null
              break
          }

          return {
            ...user,
            isBanned: true,
            banExpiration: expirationDate ? expirationDate.toISOString().split("T")[0] : null,
          }
        }
        return user
      }),
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>유저 관리</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Label htmlFor="user-select">유저 선택</Label>
            <Select onValueChange={setSelectedUser} value={selectedUser}>
              <SelectTrigger>
                <SelectValue placeholder="유저를 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                {users.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.username}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="ban-duration">제재 기간</Label>
            <Select onValueChange={setBanDuration} value={banDuration}>
              <SelectTrigger>
                <SelectValue placeholder="제재 기간을 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7days">7일</SelectItem>
                <SelectItem value="30days">30일</SelectItem>
                <SelectItem value="permanent">영구</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button onClick={handleBanUser}>유저 제재</Button>
        </div>
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-2">유저 목록</h3>
          <ul className="space-y-2">
            {users.map((user) => (
              <li key={user.id} className="flex justify-between items-center">
                <span>{user.username}</span>
                <span>
                  {user.isBanned
                    ? user.banExpiration
                      ? `제재 중 (해제: ${user.banExpiration})`
                      : "영구 제재"
                    : "정상"}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}

