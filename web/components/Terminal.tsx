"use client";

import React, { useState, useEffect, useRef } from "react";
import { Terminal as TerminalIcon, X, Maximize2, Minimize2, Circle, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogEntry {
    id: string;
    timestamp: string;
    level: "info" | "warn" | "error" | "success";
    source: string;
    message: string;
}

export const SystemTerminal = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(true);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const eventSource = new EventSource("/api/events");

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'log') {
                const newLog: LogEntry = {
                    id: data.id || Math.random().toString(36),
                    timestamp: data.timestamp || new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                    level: data.level || "info",
                    source: data.source || "SISTEMA",
                    message: data.message
                };
                setLogs(prev => [newLog, ...prev].slice(0, 100));
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, []);

    const levelStyles = {
        info: "text-slate-400",
        warn: "text-amber-500",
        error: "text-red-500 font-bold",
        success: "text-emerald-500"
    };

    if (isMinimized) {
        return (
            <button
                onClick={() => setIsMinimized(false)}
                className="fixed bottom-6 right-6 flex items-center gap-3 bg-white border border-slate-200 px-4 py-3 rounded-2xl shadow-xl shadow-slate-200 hover:border-blue-500 transition-all z-50 group transition-all duration-300"
            >
                <div className="relative">
                    <Activity size={18} className="text-blue-500" />
                    <span className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full border-2 border-white animate-pulse" />
                </div>
                <span className="text-xs font-bold text-slate-700 uppercase tracking-tight">Monitor de Actividad</span>
                <div className="h-4 w-px bg-slate-200" />
                <span className="text-[10px] font-mono text-slate-400">{logs[0]?.message.substring(0, 30) || "Escaneando mercado..."}...</span>
            </button>
        );
    }

    return (
        <div className={cn(
            "fixed bottom-6 right-6 w-[500px] h-[400px] bg-white border border-slate-200 rounded-3xl shadow-2xl shadow-slate-300 flex flex-col overflow-hidden z-50 transition-all duration-300 animate-in slide-in-from-bottom-10"
        )}>
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white">
                        <TerminalIcon size={16} />
                    </div>
                    <div>
                        <h3 className="text-xs font-black text-slate-900 uppercase">Monitor del Sistema</h3>
                        <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Logs de Protocolo v4.0</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setIsMinimized(true)}
                        className="p-1.5 hover:bg-slate-200 rounded-md transition-colors text-slate-400"
                    >
                        <Minimize2 size={14} />
                    </button>
                </div>
            </div>

            {/* Logs Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2 bg-slate-950 font-mono text-[11px] selection:bg-blue-500/30">
                {logs.length === 0 && (
                    <div className="flex items-center justify-center h-full text-slate-600 italic">
                        Esperando señal de los sniffers...
                    </div>
                )}
                {logs.map((log) => (
                    <div key={log.id} className="flex gap-3 leading-relaxed border-b border-white/5 pb-2">
                        <span className="text-slate-600 shrink-0">[{log.timestamp}]</span>
                        <span className={cn("shrink-0 uppercase font-black w-16", levelStyles[log.level])}>
                            {log.source}:
                        </span>
                        <span className="text-slate-300 break-all">{log.message}</span>
                    </div>
                ))}
                <div ref={scrollRef} />
            </div>

            {/* Footer */}
            <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 bg-slate-50 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase">
                        <Circle size={8} className="fill-emerald-500 text-emerald-500" />
                        Conexión SSE Estable
                    </div>
                </div>
                <span className="text-[10px] font-mono text-slate-400 uppercase">{logs.length} eventos registrados</span>
            </div>
        </div>
    );
};
