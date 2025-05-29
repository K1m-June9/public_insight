'use client'

import { Sun, Cloud, CloudRain } from 'lucide-react'

const weatherData = [
  { date: '16일 (수)', morning: { temp: '16°C', icon: Sun }, evening: { temp: '23°C', icon: Sun } },
  { date: '17일 (목)', morning: { temp: '14°C', icon: Sun }, evening: { temp: '24°C', icon: Cloud } },
  { date: '18일 (금)', morning: { temp: '11°C', icon: CloudRain }, evening: { temp: '19°C', icon: CloudRain } },
  { date: '19일 (토)', morning: { temp: '13°C', icon: Cloud }, evening: { temp: '23°C', icon: Sun } },
  { date: '20일 (일)', morning: { temp: '12°C', icon: Sun }, evening: { temp: '23°C', icon: Sun } },
  { date: '21일 (월)', morning: { temp: '11°C', icon: Sun }, evening: { temp: '24°C', icon: Sun } },
  { date: '22일 (화)', morning: { temp: '16°C', icon: Sun }, evening: { temp: '23°C', icon: Sun } },
  { date: '23일 (수)', morning: { temp: '10°C', icon: Cloud }, evening: { temp: '22°C', icon: Sun } },
]

export default function WeatherGrid() {
  const getIconColor = (IconComponent: typeof Sun | typeof Cloud | typeof CloudRain) => {
    if (IconComponent === Cloud) return 'text-gray-500'
    if (IconComponent === CloudRain) return 'text-blue-500'
    return 'text-yellow-500'
  }

  return (
    <div className="grid grid-cols-4 gap-2 p-4">
      {weatherData.map((day, index) => (
        <div key={index} className="border rounded-lg p-2 text-center">
          <div className="text-sm font-medium mb-1">{day.date}</div>
          <div className="grid grid-cols-2 gap-1">
            <div className="text-center">
              <div className="text-xs">오전</div>
              <day.morning.icon className={`w-6 h-6 mx-auto ${getIconColor(day.morning.icon)}`} />
              <div className="text-sm">{day.morning.temp}</div>
            </div>
            <div className="text-center">
              <div className="text-xs">오후</div>
              <day.evening.icon className={`w-6 h-6 mx-auto ${getIconColor(day.evening.icon)}`} />
              <div className="text-sm">{day.evening.temp}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

