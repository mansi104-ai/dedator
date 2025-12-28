import { type NextRequest, NextResponse } from "next/server"
import { execSync } from "child_process"
import path from "path"

export async function POST(req: NextRequest) {
  try {
    const rawData = await req.json()

    // Execute Python processor
    // We pass the data via stdin to the python script
    const scriptPath = path.join(process.cwd(), "scripts", "main.py")
    const inputJson = JSON.stringify(rawData || {})

    const pythonCommand = process.platform === "win32" ? "python" : "python3"

    const result = execSync(`${pythonCommand} "${scriptPath}"`, {
      input: inputJson,
      encoding: "utf-8",
      cwd: process.cwd(),
    })

    return NextResponse.json(JSON.parse(result))
  } catch (error: any) {
    console.error("[v0] Analytics Error:", error.message)
    return NextResponse.json({ error: "Failed to process analytics", details: error.message }, { status: 500 })
  }
}

export async function GET() {
  return NextResponse.json({ status: "healthy", timestamp: new Date().toISOString() })
}
