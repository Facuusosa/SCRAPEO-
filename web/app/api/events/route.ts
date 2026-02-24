import { NextRequest } from "next/server";

// Simple in-memory bridge for the demo
// In a real prod environment, use Redis Pub/Sub or a dedicated WebSocket server
let clients: ReadableStreamDefaultController[] = [];

export async function GET() {
    const stream = new ReadableStream({
        start(controller) {
            clients.push(controller);

            const heartbeat = setInterval(() => {
                controller.enqueue(`data: ${JSON.stringify({ type: 'heartbeat' })}\n\n`);
            }, 15000);

            // Clean up on close
            return () => {
                clearInterval(heartbeat);
                clients = clients.filter(c => c !== controller);
            };
        }
    });

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        },
    });
}

export async function POST(req: NextRequest) {
    const data = await req.json();

    // Broadcast to all connected clients
    const message = `data: ${JSON.stringify(data)}\n\n`;
    clients.forEach(client => {
        try {
            client.enqueue(message);
        } catch (e) {
            // Client probably disconnected
        }
    });

    return new Response(JSON.stringify({ success: true }), {
        headers: { 'Content-Type': 'application/json' },
    });
}
