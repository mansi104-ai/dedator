"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"

export function TestDashboard() {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const [url, setUrl] = useState("")

  const runAnalysis = async () => {
    setLoading(true)
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        body: JSON.stringify({ url: url || undefined, depth: 0 }),
      })
      const result = await res.json()
      setData(result)
    } catch (error) {
      console.error("[v0] Analysis failed:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <Card className="border-primary/20 bg-background/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="text-2xl font-bold tracking-tight">AI Analytics Testing Suite</CardTitle>
          <p className="text-muted-foreground">Trigger backend processing scripts and verify data output.</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Website URL (Optional)</label>
            <input
              type="url"
              placeholder="https://example.com"
              className="w-full p-2 border rounded-md bg-background"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <Button onClick={runAnalysis} disabled={loading} size="lg" className="w-full">
            {loading ? <Spinner className="mr-2" /> : null}
            {url ? "Scrape & Analyze Website" : "Run Default Analytics Pipeline"}
          </Button>
        </CardContent>
      </Card>

      {data && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-[400px] text-sm font-mono">
              {JSON.stringify(data, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
