"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

const data = [
  {
    year: "2020",
    일반회계: 31.87,
    특별회계: 69.4,
    사회복지: 69.77,
    사회복지2: 0,
    사회복지3: 61.01,
  },
  {
    year: "2021",
    일반회계: 33.01,
    특별회계: 15.67,
    사회복지: 95.2,
    사회복지2: 0,
    사회복지3: 88.43,
  },
  {
    year: "2022",
    일반회계: 2.34,
    특별회계: 34.64,
    사회복지: 46.32,
    사회복지2: 0,
    사회복지3: 68.39,
  },
  {
    year: "2023",
    일반회계: 13.44,
    특별회계: 72.44,
    사회복지: 80.58,
    사회복지2: 18.13,
    사회복지3: 28.12,
  },
  {
    year: "2024",
    일반회계: 92.73,
    특별회계: 71.75,
    사회복지: 63.12,
    사회복지2: 23.28,
    사회복지3: 97.39,
  },
]

const departmentColors = {
  assembly: ["#1a7f7f", "#48D1CC", "#40E0D0", "#7FFFD4", "#00CED1"],
  education: ["#1a4d1a", "#2C9C2C", "#00CC00", "#66C600", "#66B300"],
  gender: ["#8A2BE2", "#9370DB", "#BA55D3", "#DDA0DD", "#EE82EE"],
  employment: ["#8B4513", "#A0522D", "#B8860B", "#DEB887", "#D2B48C"],
  culture: ["#FFA500", "#FF8C00", "#FFD700", "#FFDAB9", "#FFEFD5"],
}

interface BudgetChartProps {
  department: "assembly" | "education" | "gender" | "employment" | "culture"
  color?: string
}

export default function BudgetChart({ department, color }: BudgetChartProps) {
  const colors = color ? [color, ...departmentColors[department].slice(1)] : departmentColors[department]

  return (
    <div className="p-4">
      <h3 className={`text-lg font-semibold text-${colors[0]} mb-4`}>연간 예산 현황</h3>
      <div className="w-full" style={{ height: "400px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(data[0])
              .filter((key) => key !== "year")
              .map((key, index) => (
                <Bar key={key} dataKey={key} stackId="a" fill={colors[index % colors.length]} />
              ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

