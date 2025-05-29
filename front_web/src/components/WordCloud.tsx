"use client"
import { useEffect, useRef, useState } from "react"
import * as d3 from "d3"
import cloud from "d3-cloud"
import { scaleLinear } from "d3-scale"
import { ChevronLeft, ChevronRight } from "lucide-react"

// 우리 애플리케이션에서 사용하는 Word 인터페이스
interface Word {
  text: string
  value: number
  size?: number
}

// d3-cloud 라이브러리의 Word 타입과 호환되는 확장 인터페이스
interface CloudWord extends cloud.Word {
  value?: number
  text: string // text 속성이 필수임을 명시
}

interface WordCloudProps {
  department: "assembly" | "education" | "gender" | "employment" | "culture"
  color?: string
}

const currentYear = new Date().getFullYear()
const yearData: Record<number, Word[]> = {
  [currentYear]: [
    { text: "정책", value: 64 },
    { text: "국회", value: 55 },
    { text: "법안", value: 41 },
    { text: "예산", value: 38 },
    { text: "의원", value: 34 },
    { text: "청문회", value: 30 },
    { text: "국정감사", value: 28 },
    { text: "상임위", value: 26 },
    { text: "본회의", value: 25 },
    { text: "입법", value: 23 },
    { text: "여야", value: 21 },
    { text: "표결", value: 19 },
    { text: "공청회", value: 18 },
    { text: "개정안", value: 17 },
    { text: "국정운영", value: 16 },
  ],
  [currentYear - 1]: [
    { text: "코로나19", value: 70 },
    { text: "경제", value: 60 },
    { text: "백신", value: 55 },
    { text: "재난지원금", value: 50 },
    { text: "비대면", value: 45 },
    { text: "정책", value: 40 },
    { text: "국회", value: 35 },
    { text: "법안", value: 30 },
    { text: "예산", value: 25 },
    { text: "의원", value: 20 },
  ],
  [currentYear - 2]: [
    { text: "선거", value: 65 },
    { text: "대통령", value: 60 },
    { text: "정책", value: 55 },
    { text: "경제", value: 50 },
    { text: "국회", value: 45 },
    { text: "법안", value: 40 },
    { text: "예산", value: 35 },
    { text: "의원", value: 30 },
    { text: "청문회", value: 25 },
    { text: "국정감사", value: 20 },
  ],
}

export default function WordCloud({ color = "#1a7f7f" }: WordCloudProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedYear, setSelectedYear] = useState(currentYear)
  const [opacity, setOpacity] = useState(1)
  const [transition, setTransition] = useState(false)

  const changeYear = (direction: "prev" | "next") => {
    setOpacity(0)
    setTransition(true)
    setTimeout(() => {
      const years = Object.keys(yearData)
        .map(Number)
        .sort((a, b) => b - a)
      const currentIndex = years.indexOf(selectedYear)
      if (direction === "prev" && currentIndex < years.length - 1) {
        setSelectedYear(years[currentIndex + 1])
      } else if (direction === "next" && currentIndex > 0) {
        setSelectedYear(years[currentIndex - 1])
      }
      setOpacity(1)
    }, 300)
  }

  useEffect(() => {
    if (transition) {
      const timer = setTimeout(() => setTransition(false), 600)
      return () => clearTimeout(timer)
    }
  }, [transition])

  useEffect(() => {
    if (svgRef.current && opacity === 1) {
      const svg = d3.select(svgRef.current)
      const width = 800
      const height = 400

      const words = yearData[selectedYear]

      const layout = cloud()
        .size([width, height])
        .words(words.map((d) => ({ ...d, size: d.value })))
        .padding(5)
        .rotate(() => ~~(Math.random() * 2) * 90)
        .font("Arial")
        .fontSize((d) => d.size || 0)
        .on("end", draw)

      layout.start()

      function draw(words: CloudWord[]) {
        svg.selectAll("*").remove()

        // 최소값과 최대값 계산 시 size 속성 사용
        const minSize = Math.min(...words.map((w) => w.size || 0))
        const maxSize = Math.max(...words.map((w) => w.size || 0))

        const colorScale = scaleLinear<string>()
          .domain([minSize, maxSize])
          .range([d3.rgb(color).brighter(1).toString(), d3.rgb(color).darker(1).toString()])

        svg
          .attr("width", layout.size()[0])
          .attr("height", layout.size()[1])
          .append("g")
          .attr("transform", `translate(${layout.size()[0] / 2 + 50},${layout.size()[1] / 2})`)
          .selectAll("text")
          .data(words)
          .enter()
          .append("text")
          .style("font-size", (d) => `${d.size}px`)
          .style("font-family", "Arial")
          .style("fill", (d) => colorScale(d.size || 0))
          .attr("text-anchor", "middle")
          .attr("transform", (d) => `translate(${d.x || 0},${d.y || 0})rotate(${d.rotate || 0})`)
          .text((d) => d.text || "") // 기본값 제공
      }
    }
  }, [color, selectedYear, opacity])

  return (
    <div className="p-4">
      <h3 className={`text-lg font-semibold mb-4 text-${color}`}>주요 키워드</h3>
      <div className="flex justify-center items-center mb-4">
        <button onClick={() => changeYear("prev")} className="p-2">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <span className="text-xl font-bold mx-4">{selectedYear}년</span>
        <button onClick={() => changeYear("next")} className="p-2">
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>
      <div
        style={{
          height: "400px",
          width: "100%",
          overflow: "hidden",
          opacity: opacity,
          transition: transition ? "opacity 0.3s ease-in-out" : "none",
        }}
      >
        <svg ref={svgRef} style={{ width: "100%", height: "100%" }}></svg>
      </div>
    </div>
  )
}

