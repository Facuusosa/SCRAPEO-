"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export function RealTimeBridge() {
    const router = useRouter();

    useEffect(() => {
        const eventSource = new EventSource("/api/events");

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // If the bridge sends an update signal (detected glitch)
            if (data.type === 'update' && data.refreshProducts) {
                console.log("Real-time update received: Refreshing market data...");
                router.refresh(); // Triggers a re-fetch of server components
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, [router]);

    return null; // Invisible component
}
