import { type NextRequest, NextResponse } from "next/server"
import { execSync } from "child_process"
import path from "path"

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { url, depth = 0 } = body

    if (!url) {
      return NextResponse.json({ error: "URL is required" }, { status: 400 })
    }

    const scriptPath = path.join(process.cwd(), "scripts", "main.py")
    const inputJson = JSON.stringify({ url, depth })

    const pythonCommand = process.platform === "win32" ? "python" : "python3"

    const result = execSync(`${pythonCommand} "${scriptPath}"`, {
      input: inputJson,
      encoding: "utf-8",
      cwd: process.cwd(),
    })

    return NextResponse.json(JSON.parse(result))
  } catch (error: any) {
    console.error("[v0] Scrape Error:", error.message)
    return NextResponse.json({ error: "Failed to scrape URL", details: error.message }, { status: 500 })
  }
}
