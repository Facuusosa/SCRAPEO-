import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

const STORE_DOMAINS: Record<string, string> = {
    "Fravega": "https://www.fravega.com",
    "OnCity": "https://www.oncity.com",
    "Cetrogar": "https://www.cetrogar.com.ar",
    "Megatone": "https://www.megatone.net",
    "Newsan": "https://www.newsan.com.ar",
    "Casa del Audio": "https://www.casadelaudio.com"
};

export function sanitizeUrl(url: string, store: string) {
    if (!url) return "#";

    let cleanUrl = url.trim();

    // Si ya es absoluta, verificar protocolo
    if (cleanUrl.startsWith("http")) return cleanUrl;

    // Manejar URLs tipo //tienda.com
    if (cleanUrl.startsWith("//")) return `https:${cleanUrl}`;

    // Manejar URLs relativas
    const domain = STORE_DOMAINS[store] || "";
    if (cleanUrl.startsWith("/")) {
        return `${domain}${cleanUrl}`;
    }

    return `${domain}/${cleanUrl}`;
}
