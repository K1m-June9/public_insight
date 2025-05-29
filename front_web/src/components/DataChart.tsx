"use client"

import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts"
import { useRouter } from "next/navigation"

const data = [
  { name: "국회", value: 928, color: "#1a4789", path: "/department/assembly" },
  { name: "교육부", value: 592, color: "#2d6cbb", path: "/department/education" },
  { name: "여성가족부", value: 428, color: "#5b9bd5", path: "/department/gender" },
  { name: "고용노동부", value: 412, color: "#9cc2e6", path: "/department/employment" },
  { name: "문화체육관광부", value: 266, color: "#c5d9f1", path: "/department/culture" },
  { name: "기타", value: 122, color: "#e8f1fa", path: "/department/others" },
]

export default function DataChart() {
  const router = useRouter()
  const totalCount = data.reduce((sum, item) => sum + item.value, 0)

  const handleClick = (entry: { path: string }) => {
    router.push(entry.path)
  }

  const renderCustomizedLabel = ({
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
      <g>
        <text x={cx} y={cy} dy={8} textAnchor="middle" fill="#333" fontSize={20}>
          {totalCount}
        </text>
        <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={data[index].color} fill="none" />
        <circle cx={ex} cy={ey} r={2} fill={data[index].color} stroke="none" />
        <text
          x={ex + (cos >= 0 ? 1 : -1) * 12}
          y={ey}
          textAnchor={textAnchor}
          fill="#333"
          fontSize={14}
          dominantBaseline="central"
          style={{ cursor: "pointer" }}
          onClick={() => handleClick(data[index])}
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
        >
          {value}
        </text>
      </g>
    )
  }

  return (
    <div className="pt-2 px-4 flex flex-col items-center">
      <div className="text-2xl font-bold text-gray-700 mb-4">&lt;2024/10/14&gt;</div>
      <div className="w-full max-w-2xl">
        <style jsx global>{`
          /* 호버 효과 */
          .pie-chart .recharts-pie-sector {
            transition: transform 0.3s ease-out;
            transform-origin: center;
          }
          
          .pie-chart .recharts-pie-sector:hover {
            transform: scale(1.05);
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
              className="pie-chart"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

