import { NextRequest, NextResponse } from "next/server";

const TUNARA_AI_URL =
  process.env.TUNARA_AI_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const response = await fetch(`${TUNARA_AI_URL}/api/prompt-director`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const payload = await response.json();

    if (!response.ok) {
      return NextResponse.json(payload, { status: response.status });
    }

    return NextResponse.json(payload);
  } catch (error) {
    console.error("Unable to call Prompt Director:", error);
    return NextResponse.json(
      { message: "Unable to contact Tunara AI." },
      { status: 502 }
    );
  }
}
