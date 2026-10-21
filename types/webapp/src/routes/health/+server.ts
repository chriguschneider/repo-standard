import { json } from '@sveltejs/kit';
import { VERSION } from '#lib/version.ts';

// Liveness for Docker's HEALTHCHECK and the reverse proxy. No database
// access on purpose: a locked database must not restart the container.
export function GET() {
  return json({ status: 'ok', version: VERSION });
}
