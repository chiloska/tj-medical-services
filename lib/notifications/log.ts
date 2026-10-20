// One JSON line per event, so Vercel logs can be searched by "event".
export function log(event: string, data: Record<string, unknown> = {}): void {
  console.log(JSON.stringify({ event, ...data }));
}

export function json(body: unknown, status = 200): Response {
  return Response.json(body, { status });
}
