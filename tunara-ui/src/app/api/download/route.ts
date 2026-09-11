import { NextRequest, NextResponse } from "next/server";

const ALLOWED_HOSTS = new Set(["localhost", "127.0.0.1"]);

export async function GET(request: NextRequest) {
  const source = request.nextUrl.searchParams.get("url");
  const requestedName = request.nextUrl.searchParams.get("name") ?? "tunara-file";

  if (!source) {
    return NextResponse.json({ message: "Missing download URL" }, { status: 400 });
  }

  let sourceUrl: URL;
  try {
    sourceUrl = new URL(source);
  } catch {
    return NextResponse.json({ message: "Invalid download URL" }, { status: 400 });
  }

  if (!ALLOWED_HOSTS.has(sourceUrl.hostname)) {
    return NextResponse.json({ message: "Download host is not allowed" }, { status: 403 });
  }

  const response = await fetch(sourceUrl, { cache: "no-store" });
  if (!response.ok || !response.body) {
    return NextResponse.json(
      { message: `Unable to download source file. HTTP ${response.status}` },
      { status: 502 }
    );
  }

  const safeName = requestedName.replace(/[^A-Za-z0-9._-]+/g, "-");
  const headers = new Headers();
  headers.set("Content-Type", response.headers.get("Content-Type") ?? "application/octet-stream");
  headers.set("Content-Disposition", `attachment; filename="${safeName}"`);

  const contentLength = response.headers.get("Content-Length");
  if (contentLength) {
    headers.set("Content-Length", contentLength);
  }

  return new NextResponse(response.body, { status: 200, headers });
}
