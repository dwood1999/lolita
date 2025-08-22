import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Proxy Server-Sent Events stream from Python service to avoid CORS/hardcoded domains
export const GET: RequestHandler = async ({ params, fetch, setHeaders }) => {
    const { id } = params;
    const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

    const upstream = await fetch(`${PYTHON_SERVICE_URL}/analysis/${id}/progress`, {
        headers: {
            Accept: 'text/event-stream'
        }
    });

    if (!upstream.ok) {
        return new Response(`Upstream error: ${upstream.statusText}`, { status: upstream.status });
    }

    // Pass through SSE headers
    setHeaders({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive'
    });

    return new Response(upstream.body, {
        status: 200
    });
};


