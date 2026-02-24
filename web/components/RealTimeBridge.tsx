"use client";

import { useEffect } from "react";

export function RealTimeBridge() {
    useEffect(() => {
        const eventSource = new EventSource("/api/events");

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Priority 4: Eliminamos router.refresh() para evitar parpadeos molestos (flicker).
            // La actualización ahora es manejada localmente por los componentes (Optimistic UI).
            if (data.type === 'update') {
                console.log("Evento en tiempo real detectado. Procesando en UI optimista...");
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, []);

    return null; // Componente invisible de orquestación
}
