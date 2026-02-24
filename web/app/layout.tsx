import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { SystemTerminal } from "@/components/Terminal";
import { RealTimeBridge } from "@/components/RealTimeBridge";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Odiseo | Inteligencia de Mercado",
  description: "Sistema avanzado de arbitraje y monitoreo de precios",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased font-sans bg-slate-50 text-slate-900`}
      >
        <Sidebar />
        <div className="min-h-screen">
          {children}
        </div>
        <SystemTerminal />
        <RealTimeBridge />
      </body>
    </html>
  );
}
