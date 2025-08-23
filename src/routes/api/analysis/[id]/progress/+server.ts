import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Proxy Server-Sent Events stream from Python service with improved error handling
export const GET: RequestHandler = async ({ params, setHeaders }) => {
    const { id } = params;
    const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

    console.log(`🔄 Proxying progress stream for analysis: ${id}`);

    try {
        // Set SSE headers immediately
        setHeaders({
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*'
        });

        // Use fetch with timeout and proper error handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        const upstream = await fetch(`${PYTHON_SERVICE_URL}/analysis/${id}/progress`, {
            headers: {
                Accept: 'text/event-stream',
                'Cache-Control': 'no-cache'
            },
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!upstream.ok) {
            console.error(`❌ Upstream error: ${upstream.status} ${upstream.statusText}`);
            
            // Return a proper SSE error stream
            const errorStream = new ReadableStream({
                start(controller) {
                    const errorData = JSON.stringify({
                        stage: 'error',
                        progress: 0,
                        message: `Connection error: ${upstream.statusText}`,
                        timestamp: Date.now()
                    });
                    controller.enqueue(`data: ${errorData}\n\n`);
                    controller.close();
                }
            });

            return new Response(errorStream, {
                status: 200,
                headers: {
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            });
        }

        // Create a new readable stream that handles errors
        const enhancedStream = new ReadableStream({
            async start(controller) {
                try {
                    const reader = upstream.body?.getReader();
                    if (!reader) {
                        throw new Error('No response body');
                    }

                    let lastHeartbeat = Date.now();
                    
                    // Send initial heartbeat
                    const heartbeat = JSON.stringify({
                        heartbeat: true,
                        timestamp: Date.now()
                    });
                    controller.enqueue(`data: ${heartbeat}\n\n`);

                    while (true) {
                        const { done, value } = await reader.read();
                        
                        if (done) {
                            console.log(`✅ Progress stream completed for ${id}`);
                            break;
                        }

                        if (value) {
                            controller.enqueue(value);
                            lastHeartbeat = Date.now();
                        }

                        // Send heartbeat if no data for 10 seconds
                        if (Date.now() - lastHeartbeat > 10000) {
                            const heartbeat = JSON.stringify({
                                heartbeat: true,
                                timestamp: Date.now()
                            });
                            controller.enqueue(`data: ${heartbeat}\n\n`);
                            lastHeartbeat = Date.now();
                        }
                    }
                } catch (error) {
                    console.error(`❌ Stream error for ${id}:`, error);
                    
                    // Send error message to client
                    const errorData = JSON.stringify({
                        stage: 'error',
                        progress: 0,
                        message: 'Connection lost. Analysis may still be running. Please check the screenplays page.',
                        timestamp: Date.now()
                    });
                    controller.enqueue(`data: ${errorData}\n\n`);
                } finally {
                    controller.close();
                }
            }
        });

        return new Response(enhancedStream, {
            status: 200
        });

    } catch (error) {
        console.error(`❌ Progress proxy error for ${id}:`, error);
        
        // Return error as SSE stream
        const errorStream = new ReadableStream({
            start(controller) {
                const errorData = JSON.stringify({
                    stage: 'error',
                    progress: 0,
                    message: 'Failed to connect to analysis service. Please try again or check the screenplays page.',
                    timestamp: Date.now()
                });
                controller.enqueue(`data: ${errorData}\n\n`);
                controller.close();
            }
        });

        return new Response(errorStream, {
            status: 200,
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        });
    }
};


