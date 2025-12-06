import type React from "react"
import type { Metadata } from "next"
import { Suspense } from "react"
import "./globals.css"
import Loading from "./loading"

export const metadata: Metadata = {
  title: "Hygeia AI - Your Health Companion",
  description: "Advanced AI-powered health companion for personalized medical insights",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <Suspense fallback={<Loading />}>{children}</Suspense>
      </body>
    </html>
  )
}
