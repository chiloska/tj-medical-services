// Idempotency keys. Uses Upstash Redis (REST) when configured, otherwise a per-instance in-memory map,
// which only catches redeliveries that land on the same warm serverless instance.
import { log } from './log';

const TTL_SECONDS = 24 * 60 * 60;
const memory = new Map<string, number>(); // key -> expiry (ms)

function redisConfig() {
  // Upstash's own names, or the ones the Vercel Marketplace integration sets.
  const url = process.env.UPSTASH_REDIS_REST_URL ?? process.env.KV_REST_API_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN ?? process.env.KV_REST_API_TOKEN;
  return url && token ? { url, token } : undefined;
}

async function redis(command: string[]): Promise<unknown> {
  const cfg = redisConfig()!;
  const res = await fetch(cfg.url, {
    method: 'POST',
    headers: { Authorization: `Bearer ${cfg.token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(command),
  });
  if (!res.ok) throw new Error(`redis HTTP ${res.status}`);
  return ((await res.json()) as { result?: unknown }).result;
}

/** True if this caller is the first to claim the key (go ahead and send); false if it was already claimed. */
export async function claim(key: string): Promise<boolean> {
  if (redisConfig()) {
    try {
      return (await redis(['SET', key, '1', 'NX', 'EX', String(TTL_SECONDS)])) === 'OK';
    } catch (err) {
      log('dedupe.redis_error', { error: (err as Error).message }); // fall back to memory rather than drop the message
    }
  }
  const now = Date.now();
  const expiry = memory.get(key);
  if (expiry !== undefined && expiry > now) return false;
  memory.set(key, now + TTL_SECONDS * 1000);
  return true;
}

/** Undo a claim when the send did not happen, so a retry or redelivery can try again. */
export async function release(key: string): Promise<void> {
  memory.delete(key);
  if (redisConfig()) {
    try {
      await redis(['DEL', key]);
    } catch (err) {
      log('dedupe.redis_error', { error: (err as Error).message });
    }
  }
}
