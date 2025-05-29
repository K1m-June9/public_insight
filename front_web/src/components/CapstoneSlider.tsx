"use client"

import { useState, useEffect, useCallback } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

const capstoneProjects = [
  {
    id: "1",
    title: "요약 및 키워드 추출",
    description: "시간개오래걸림 ㄹㅇ..;;",
    image: "/capstone1.jpg",
  },
  {
    id: "2",
    title: "AWS 클라우드",
    description:
      "유료서버~~",
    image: "/capstone2.jpg",
  },
  {
    id: "3",
    title: "React, tailwind css 사용",
    description: "좋긴한데 너무 무겁고 어렵고 와랄랄랄",
    image: "/capstone3.jpg",
  },
]

export default function CapstoneSlider() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showControls, setShowControls] = useState(false)

  // 의존성 배열에서 capstoneProjects.length 제거
  const nextSlide = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % capstoneProjects.length)
  }, [])

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + capstoneProjects.length) % capstoneProjects.length)
  }

  useEffect(() => {
    const timer = setInterval(() => {
      nextSlide()
    }, 5000)

    return () => clearInterval(timer)
  }, [nextSlide])

  return (
    <div
      className="relative mb-4 bg-white shadow-md rounded-lg p-4"
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
    >
      <div className="h-[220px]">
        <Link href={`/capstone/${capstoneProjects[currentIndex].id}`}>
          <h2 className="text-xl font-semibold mb-2">{capstoneProjects[currentIndex].title}</h2>
          <div className="relative h-[150px] mb-2">
            <Image
              src={capstoneProjects[currentIndex].image || "/placeholder.svg"}
              alt={capstoneProjects[currentIndex].title}
              fill
              style={{ objectFit: "cover" }}
              className="rounded-lg"
            />
          </div>
          <p className="text-sm text-gray-600 line-clamp-2">{capstoneProjects[currentIndex].description}</p>
        </Link>
        <button
          onClick={prevSlide}
          className={`absolute left-2 top-[75px] p-2 rounded-full bg-white/80 hover:bg-white shadow transition-opacity duration-200 ${
            showControls ? "opacity-100" : "opacity-0"
          }`}
          aria-label="Previous project"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button
          onClick={nextSlide}
          className={`absolute right-2 top-[75px] p-2 rounded-full bg-white/80 hover:bg-white shadow transition-opacity duration-200 ${
            showControls ? "opacity-100" : "opacity-0"
          }`}
          aria-label="Next project"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>
      <div
        className={`flex justify-center gap-2 mt-2 transition-opacity duration-200 ${showControls ? "opacity-100" : "opacity-0"}`}
      >
        {capstoneProjects.map((_, index) => (
          <button
            key={index}
            className={`w-2 h-2 rounded-full ${index === currentIndex ? "bg-blue-600" : "bg-gray-300"}`}
            onClick={() => setCurrentIndex(index)}
          />
        ))}
      </div>
    </div>
  )
}

