"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Send, Loader2, FileText, AlertCircle, Upload } from "lucide-react"
import { SidebarNav } from "@/components/sidebar-nav"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { fetchAPI } from "@/lib/api"

type Message = {
  role: "user" | "assistant"
  content: string
}

type Document = {
  filename: string
  id?: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedDocs, setSelectedDocs] = useState<string[]>([])
  const [sessionId] = useState(() => crypto.randomUUID())
  const [documentsError, setDocumentsError] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append("file", file)

    try {
      await fetchAPI("/documents/upload", {
        method: "POST",
        body: formData,
      })
      fetchDocuments()
    } catch (error) {
      console.error("Upload failed:", error)
      alert("Failed to upload document")
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const fetchDocuments = async () => {
    try {
      const data = await fetchAPI("/documents")
      setDocuments(data.documents || data || [])
      setDocumentsError(false)
    } catch (error) {
      console.error("[v0] Failed to fetch documents:", error)
      setDocumentsError(true)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput("")
    setMessages((prev) => [...prev, { role: "user", content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetchAPI("/chat", {
        method: "POST",
        body: JSON.stringify({
          query: userMessage,
          session_id: sessionId,
          doc_filters: selectedDocs,
        }),
      })

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer || response.response || "No response" },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please make sure the backend is running." },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleDocument = (docName: string) => {
    setSelectedDocs((prev) => (prev.includes(docName) ? prev.filter((d) => d !== docName) : [...prev, docName]))
  }

  return (
    <div className="flex min-h-screen bg-background">
      <SidebarNav onCollapseChange={setIsSidebarCollapsed} />

      <main className={`flex-1 flex transition-all duration-300 ${isSidebarCollapsed ? "ml-20" : "ml-64"}`}>
        {/* Chat Area */}
        <div className="flex-1 flex flex-col p-6">
          <Card className="flex-1 flex flex-col shadow-lg">
            <CardHeader className="border-b">
              <CardTitle className="text-2xl">AI Medical Assistant</CardTitle>
              <p className="text-sm text-muted-foreground">Ask me anything about your health</p>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col p-6 gap-4 overflow-hidden">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4">
                {messages.length === 0 && (
                  <div className="h-full flex items-center justify-center text-center text-muted-foreground">
                    <div>
                      <p className="text-lg mb-2">Welcome to Hygeia AI</p>
                      <p className="text-sm">Start a conversation to get personalized health insights</p>
                    </div>
                  </div>
                )}

                {messages.map((message, index) => (
                  <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[70%] rounded-2xl px-4 py-3 ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
                        }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-2xl px-4 py-3 flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm text-muted-foreground">Thinking...</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1"
                  disabled={isLoading}
                />
                <Button onClick={handleSend} disabled={isLoading || !input.trim()} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Knowledge Base Sidebar */}
        <div className="w-80 p-6 border-l">
          <Card className="h-full shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Active Knowledge Base
              </CardTitle>
              <p className="text-xs text-muted-foreground">Select documents to include</p>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="mb-4">
                <input
                  type="file"
                  accept=".pdf"
                  ref={fileInputRef}
                  className="hidden"
                  onChange={handleUpload}
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full"
                  disabled={isUploading}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload PDF
                    </>
                  )}
                </Button>
              </div>

              {documentsError ? (
                <div className="space-y-3">
                  <div className="flex items-start gap-2 p-3 bg-red-50 text-red-700 rounded-lg">
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <div className="text-xs">
                      <p className="font-medium mb-1">Backend not connected</p>
                      <p>Make sure your backend server is running on localhost:8000</p>
                    </div>
                  </div>
                  <Button onClick={fetchDocuments} variant="outline" size="sm" className="w-full bg-transparent">
                    Retry Connection
                  </Button>
                </div>
              ) : documents.length === 0 ? (
                <p className="text-sm text-muted-foreground">No documents available</p>
              ) : (
                documents.map((doc) => (
                  <div key={doc.filename} className="flex items-center gap-2">
                    <Checkbox
                      id={doc.filename}
                      checked={selectedDocs.includes(doc.filename)}
                      onCheckedChange={() => toggleDocument(doc.filename)}
                    />
                    <label
                      htmlFor={doc.filename}
                      className="text-sm cursor-pointer flex-1 truncate"
                      title={doc.filename}
                    >
                      {doc.filename}
                    </label>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
