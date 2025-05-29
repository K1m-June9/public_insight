"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

type CapstonePost = {
  id: string
  title: string
  tag: string
  author: string
  image: string
  content: string
}

export default function CapstoneManagement() {
  const [capstonePostsCount, setCapstonePostsCount] = useState(3)
  const [capstoneForm, setCapstoneForm] = useState<CapstonePost>({
    id: "",
    title: "",
    tag: "",
    author: "",
    image: "",
    content: "",
  })
  const [capstonePosts, setCapstonePosts] = useState<CapstonePost[]>([
    {
      id: "1",
      title: "캡스톤 프로젝트 1",
      tag: "공지사항",
      author: "관리자",
      image: "/capstone1.jpg",
      content: "내용 1",
    },
    { id: "2", title: "캡스톤 프로젝트 2", tag: "진행중", author: "팀A", image: "/capstone2.jpg", content: "내용 2" },
    { id: "3", title: "캡스톤 프로젝트 3", tag: "완료", author: "팀B", image: "/capstone3.jpg", content: "내용 3" },
  ])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setCapstoneForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (capstonePostsCount >= 5) {
      alert("등록개수 초과")
      return
    }
    const newPost = { ...capstoneForm, id: Date.now().toString() }
    setCapstonePosts((prev) => [...prev, newPost])
    setCapstonePostsCount((prev) => prev + 1)
    setCapstoneForm({ id: "", title: "", tag: "", author: "", image: "", content: "" })
  }

  const handleDelete = (id: string) => {
    setCapstonePosts((prev) => prev.filter((post) => post.id !== id))
    setCapstonePostsCount((prev) => prev - 1)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>캡스톤 게시물 관리</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">제목</Label>
            <Input id="title" name="title" value={capstoneForm.title} onChange={handleInputChange} required />
          </div>
          <div>
            <Label htmlFor="tag">태그</Label>
            <Select name="tag" onValueChange={(value) => setCapstoneForm((prev) => ({ ...prev, tag: value }))}>
              <SelectTrigger>
                <SelectValue placeholder="태그를 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="공지사항">공지사항</SelectItem>
                <SelectItem value="진행중">진행중</SelectItem>
                <SelectItem value="완료">완료</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="author">작성자</Label>
            <Input id="author" name="author" value={capstoneForm.author} onChange={handleInputChange} required />
          </div>
          <div>
            <Label htmlFor="image">사진 URL</Label>
            <Input id="image" name="image" value={capstoneForm.image} onChange={handleInputChange} required />
          </div>
          <div>
            <Label htmlFor="content">본문 내용</Label>
            <Textarea id="content" name="content" value={capstoneForm.content} onChange={handleInputChange} required />
          </div>
          <Button type="submit">게시물 추가</Button>
        </form>
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-2">캡스톤 게시물 목록</h3>
          <ul className="space-y-2">
            {capstonePosts.map((post) => (
              <li key={post.id} className="flex justify-between items-center">
                <span>{post.title}</span>
                <Button variant="destructive" onClick={() => handleDelete(post.id)}>
                  삭제
                </Button>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}

