"use client";

import React from "react";
import { motion } from "framer-motion";
import { Zap, Bell, Shield, TrendingUp, Check, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-[#030305] text-white selection:bg-emerald-500/30 font-sans">
            {/* Navbar */}
            <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-[#030305]/80 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                    <div className="text-2xl font-black tracking-tighter">
                        ODISEO<span className="text-emerald-500">.</span>
                    </div>
                    <div className="hidden md:flex gap-8 text-sm font-medium text-slate-400">
                        <a href="#features" className="hover:text-white transition-colors">Features</a>
                        <a href="#pricing" className="hover:text-white transition-colors">Precios</a>
                        <a href="#about" className="hover:text-white transition-colors">Metodología</a>
                    </div>
                    <div className="flex gap-4">
                        <Link href="/login" className="px-6 py-2.5 text-sm font-bold border border-white/10 rounded-full hover:bg-white/5 transition-all">
                            Login
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-40 pb-20 overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[600px] bg-emerald-500/10 blur-[120px] rounded-full opacity-50 pointer-events-none" />

                <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-emerald-400 text-xs font-bold uppercase tracking-widest mb-8"
                    >
                        <Zap size={14} className="fill-emerald-400" />
                        SaaS de Arbitraje v2.0 Live en Argentina
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.9] mb-8"
                    >
                        DESCUBRÍ <span className="text-emerald-500">GLITCHES</span> <br />
                        & GANÁ EN REAL-TIME.
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="max-w-2xl mx-auto text-slate-400 text-lg md:text-xl mb-12 font-medium leading-relaxed"
                    >
                        Odiseo monitorea 6 gigantes del retail las 24hs. No solo vemos el precio; validamos stock en vivo y calculamos tu margen de reventa neto.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="flex flex-col sm:flex-row gap-4 justify-center"
                    >
                        <Link href="#pricing" className="px-10 py-5 bg-emerald-500 text-black font-black rounded-2xl hover:bg-emerald-400 hover:scale-[1.02] transition-all flex items-center justify-center gap-2 group shadow-[0_0_30px_rgba(16,185,129,0.3)]">
                            EMPEZAR AHORA
                            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <Link href="/market" className="px-10 py-5 bg-white/5 border border-white/10 text-white font-bold rounded-2xl hover:bg-white/10 transition-all flex items-center justify-center">
                            Ver Catálogo Live
                        </Link>
                    </motion.div>
                </div>
            </section>

            {/* Features Grid */}
            <section id="features" className="py-24 bg-white/[0.02]">
                <div className="max-w-7xl mx-auto px-6">
                    <h2 className="text-4xl font-black mb-16 tracking-tight">INFRAESTRUCTURA DE <br />GRADO FINANCIERO.</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<Bell className="text-emerald-400" />}
                            title="Alertas Telegram VIP"
                            description="Recibí notificaciones instántaneas cuando detectamos un gap de mercado > 15%."
                        />
                        <FeatureCard
                            icon={<Shield className="text-emerald-400" />}
                            title="Stock Validator V2"
                            description="Nuestros workers simulan 'Add to Cart' para asegurar que el glitch sea real antes de alertar."
                        />
                        <FeatureCard
                            icon={<TrendingUp className="text-emerald-400" />}
                            title="Margen Odiseo"
                            description="Cálculos automáticos con costos de logística y comisiones para ver tu ganancia real."
                        />
                    </div>
                </div>
            </section>

            {/* Pricing */}
            <section id="pricing" className="py-24 overflow-hidden relative">
                <div className="max-w-7xl mx-auto px-6 relative z-10">
                    <div className="text-center mb-20">
                        <h2 className="text-5xl font-black mb-6 tracking-tight">ELEGÍ TU PLAN DE ACCIÓN</h2>
                        <p className="text-slate-400 font-medium">Acceso inmediato post-pago vía Stripe.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                        {/* VIP Plan */}
                        <div className="relative group">
                            <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 rounded-[40px] blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
                            <div className="relative bg-[#0f0f11] border border-white/10 p-10 rounded-[40px] flex flex-col h-full">
                                <div className="text-emerald-400 font-black tracking-widest text-xs uppercase mb-4">Recomendado Entry</div>
                                <h3 className="text-3xl font-black mb-2">Canal VIP Telegram</h3>
                                <div className="text-5xl font-black mb-8">$30.000 <span className="text-xl text-slate-500 font-medium">/mes</span></div>

                                <ul className="space-y-4 mb-10 flex-grow">
                                    <PriceItem text="Alertas Real-time de Glitches" />
                                    <PriceItem text="Gap > 18% Confirmado" />
                                    <PriceItem text="Validation via Playwright" />
                                    <PriceItem text="Soporte 24/7" />
                                </ul>

                                <button className="w-full py-5 bg-white text-black font-black rounded-2xl hover:scale-[1.02] transition-all">
                                    COMPRAR ACCESO VIP
                                </button>
                            </div>
                        </div>

                        {/* PRO Plan */}
                        <div className="relative group">
                            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-[40px] blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
                            <div className="relative bg-[#0f0f11] border border-white/10 p-10 rounded-[40px] flex flex-col h-full">
                                <div className="text-blue-400 font-black tracking-widest text-xs uppercase mb-4">Inversor Profesional</div>
                                <h3 className="text-3xl font-black mb-2">Mercado Pro</h3>
                                <div className="text-5xl font-black mb-8">$100.000 <span className="text-xl text-slate-500 font-medium">/mes</span></div>

                                <ul className="space-y-4 mb-10 flex-grow">
                                    <PriceItem text="Acceso a Dashboard Completo" />
                                    <PriceItem text="Filtros Tácticos de Arbitraje" />
                                    <PriceItem text="Multi-tienda (6+ targets)" />
                                    <PriceItem text="API Market Pro Access" />
                                    <PriceItem text="Canal VIP Incluido" />
                                </ul>

                                <button className="w-full py-5 bg-emerald-500 text-black font-black rounded-2xl hover:scale-[1.02] transition-all">
                                    UPGRADE A PROFESIONAL
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="h-60 flex items-center justify-center border-t border-white/5 opacity-50 text-xs font-bold tracking-[8px] uppercase">
                © 2026 ODISEO STRATEGIC INTELLIGENCE · CÓMPUTO FINANCIERO
            </footer>
        </div>
    );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
    return (
        <div className="bg-[#0f0f11] border border-white/5 p-8 rounded-[32px] hover:border-emerald-500/30 transition-all group">
            <div className="w-14 h-14 bg-emerald-500/5 rounded-2xl flex items-center justify-center mb-6 border border-emerald-500/10 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <h4 className="text-xl font-black mb-3">{title}</h4>
            <p className="text-slate-500 font-medium leading-relaxed">{description}</p>
        </div>
    );
}

function PriceItem({ text }: { text: string }) {
    return (
        <li className="flex items-center gap-3">
            <div className="w-6 h-6 bg-emerald-500/10 rounded-full flex items-center justify-center">
                <Check size={14} className="text-emerald-500" />
            </div>
            <span className="text-slate-300 font-medium">{text}</span>
        </li>
    );
}
