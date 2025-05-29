"use client"

import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts"
import { useMemo, memo, useCallback } from "react"

const data = [
  { name: "분류 1", value: 928, color: "#1a7f7f" },
  { name: "분류 2", value: 592, color: "#48D1CC" },
  { name: "분류 3", value: 428, color: "#40E0D0" },
  { name: "분류 4", value: 412, color: "#7FFFD4" },
  { name: "분류 5", value: 266, color: "#00CED1" },
  { name: "기타", value: 122, color: "#E0FFFF" },
]

interface AssemblyDepartmentChartProps {
  onCategorySelect: (category: string) => void
  selectedCategory: string | null
}

// 컴포넌트를 memo로 감싸서 불필요한 리렌더링 방지
const AssemblyDepartmentChart = memo(({ onCategorySelect, selectedCategory }: AssemblyDepartmentChartProps) => {
  // 총 개수 계산을 useMemo로 최적화
  const totalCount = useMemo(() => data.reduce((sum, item) => sum + item.value, 0), [])

  // 클릭 핸들러를 useCallback으로 최적화
  const handleClick = useCallback(
    (entry: { name: string }) => {
      onCategorySelect(entry.name)
    },
    [onCategorySelect],
  )

  // 커스텀 라벨 렌더링 함수를 useMemo로 최적화
  const renderCustomizedLabel = useCallback(
    ({
      cx,
      cy,
      midAngle,
      //innerRadius,
      outerRadius,
      index,
      name,
      value,
    }: {
      cx: number
      cy: number
      midAngle: number
      innerRadius: number
      outerRadius: number
      index: number
      name: string
      value: number
    }) => {
      const RADIAN = Math.PI / 180
      // radius 변수는 사용되지 않으므로 제거
      const sin = Math.sin(-midAngle * RADIAN)
      const cos = Math.cos(-midAngle * RADIAN)
      const sx = cx + (outerRadius + 10) * cos
      const sy = cy + (outerRadius + 10) * sin
      const mx = cx + (outerRadius + 30) * cos
      const my = cy + (outerRadius + 30) * sin
      const ex = mx + (cos >= 0 ? 1 : -1) * 22
      const ey = my

      const textAnchor = cos >= 0 ? "start" : "end"

      return (
        <g key={`label-${index}`} className="chart-label" style={{ transition: "all 0.3s ease" }}>
          <text x={cx} y={cy} dy={8} textAnchor="middle" fill="#333" fontSize={20} className="total-count">
            {totalCount}
          </text>
          <path
            d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`}
            stroke={data[index].color}
            fill="none"
            className="label-line"
          />
          <circle cx={ex} cy={ey} r={2} fill={data[index].color} stroke="none" className="label-dot" />
          <text
            x={ex + (cos >= 0 ? 1 : -1) * 12}
            y={ey}
            textAnchor={textAnchor}
            fill="#333"
            fontSize={14}
            dominantBaseline="central"
            style={{ cursor: "pointer", fontWeight: selectedCategory === name ? "bold" : "normal" }}
            onClick={() => handleClick(data[index])}
            className="label-text"
          >
            {name}
          </text>
          <text
            x={ex + (cos >= 0 ? 1 : -1) * 12}
            y={ey + 20}
            textAnchor={textAnchor}
            fill="#666"
            fontSize={12}
            dominantBaseline="central"
            className="label-value"
          >
            {value}
          </text>
        </g>
      )
    },
    [selectedCategory, handleClick, totalCount],
  )

  // 셀 데이터를 useMemo로 최적화
  const cellData = useMemo(
    () =>
      data.map((entry, index) => (
        <Cell
          key={`cell-${entry.name}`}
          fill={entry.color}
          opacity={selectedCategory === null || selectedCategory === entry.name ? 1 : 0.5}
          className={`pie-sector ${selectedCategory === entry.name ? "selected" : ""}`}
        />
      )),
    [selectedCategory],
  )

  return (
    <div className="pt-2 px-4 flex justify-center">
      <style jsx global>{`
        .pie-sector {
          transition: transform 0.3s ease-out, opacity 0.3s ease;
          transform-origin: center;
        }
        .pie-sector:hover {
          transform: scale(1.05);
        }
        .pie-sector.selected {
          transform: scale(1.05);
        }
        .chart-label {
          transition: opacity 0.3s ease, transform 0.3s ease;
        }
        .label-line, .label-dot, .label-text, .label-value, .total-count {
          transition: all 0.3s ease;
        }
        .recharts-layer {
          transition: opacity 0.3s ease;
        }
        /* 포커스 아웃라인 제거 */
        .recharts-pie-sector:focus {
          outline: none;
        }
        .recharts-pie-sector {
          outline: none;
        }
        text:focus, path:focus, circle:focus {
          outline: none;
        }
      `}</style>
      <div className="w-full max-w-2xl">
        <h2 className="text-2xl font-bold text-center mb-4 text-[#1a7f7f]">국회</h2>
        <ResponsiveContainer width="100%" height={550}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={120}
              outerRadius={190}
              fill="#8884d8"
              paddingAngle={1}
              dataKey="value"
              labelLine={false}
              label={renderCustomizedLabel}
              onClick={(entry) => handleClick(entry)}
              cursor="pointer"
              isAnimationActive={false}
            >
              {cellData}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
})

// 컴포넌트 표시 이름 설정
AssemblyDepartmentChart.displayName = "AssemblyDepartmentChart"

export default AssemblyDepartmentChart

