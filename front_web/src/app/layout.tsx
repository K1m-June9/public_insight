import "./globals.css"
import { Inter } from "next/font/google"
import { AuthProvider } from "../contexts/AuthContext"
import type React from "react" // Added import for React

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Public Insight",
  description: "Explore public policies and insights",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} custom-scrollbar`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}

