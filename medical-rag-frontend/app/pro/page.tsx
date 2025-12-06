"use client"

import { useState } from "react"
import { SidebarNav } from "@/components/sidebar-nav"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Crown, Check, Upload, Headphones, Zap, Shield } from "lucide-react"

const proFeatures = [
  {
    icon: Upload,
    title: "Unlimited Uploads",
    description: "Upload unlimited medical documents and reports",
  },
  {
    icon: Headphones,
    title: "Priority Support",
    description: "Get 24/7 priority customer support",
  },
  {
    icon: Zap,
    title: "Advanced AI Models",
    description: "Access to latest and most accurate AI models",
  },
  {
    icon: Shield,
    title: "Enhanced Privacy",
    description: "Enterprise-grade encryption and data protection",
  },
]

export default function ProVersionPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  return (
    <div className="flex min-h-screen bg-background">
      <SidebarNav onCollapseChange={setIsSidebarCollapsed} />

      <main className={`flex-1 p-6 transition-all duration-300 ${isSidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 mb-4">
              <Crown className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold mb-2">Upgrade to Pro</h1>
            <p className="text-xl text-muted-foreground">Unlock the full potential of Hygeia AI</p>
          </div>

          <Card className="shadow-xl mb-8 border-2 border-primary">
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-3xl">Pro Plan</CardTitle>
              <div className="mt-4">
                <span className="text-5xl font-bold">$29</span>
                <span className="text-muted-foreground">/month</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {proFeatures.map((feature, idx) => {
                  const Icon = feature.icon
                  return (
                    <div key={idx} className="flex items-start gap-3 p-4 rounded-lg bg-muted/50">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold mb-1">{feature.title}</h3>
                        <p className="text-sm text-muted-foreground">{feature.description}</p>
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="space-y-3 pt-4">
                <h3 className="font-semibold text-lg">Everything in Free, plus:</h3>
                <div className="space-y-2">
                  {[
                    "Unlimited document storage",
                    "Advanced health analytics",
                    "Custom health goals and tracking",
                    "API access for integrations",
                    "Export all your data anytime",
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <Check className="h-5 w-5 text-green-600" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <Button className="w-full h-12 text-lg" size="lg">
                Upgrade to Pro
              </Button>

              <p className="text-center text-sm text-muted-foreground">30-day money-back guarantee • Cancel anytime</p>
            </CardContent>
          </Card>

          <Card className="shadow-lg bg-muted/30">
            <CardContent className="p-6">
              <h3 className="font-semibold mb-2">Need Enterprise?</h3>
              <p className="text-sm text-muted-foreground mb-4">
                For healthcare organizations, hospitals, and clinics with custom requirements.
              </p>
              <Button variant="outline">Contact Sales</Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
