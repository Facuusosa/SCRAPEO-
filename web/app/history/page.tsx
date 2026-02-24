
import { History, Search } from "lucide-react";

export default function HistoryPage() {
    return (
        <main className="min-h-screen pl-64 bg-slate-50">
            <div className="bg-white border-b border-slate-200 px-10 py-12">
                <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 bg-amber-500 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-amber-100">
                        <History size={24} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase">Historial de Alertas</h1>
                        <p className="text-slate-500 font-medium tracking-tight">Registro completo de todos los movimientos de precios detectados.</p>
                    </div>
                </div>
            </div>

            <div className="p-10">
                <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden pro-shadow">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 border-b border-slate-200">
                            <tr>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Fecha</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Producto</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Tienda</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Variación</th>
                                <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Estado</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            <tr className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 text-xs font-medium text-slate-500">Hace 12 min</td>
                                <td className="px-6 py-4 text-xs font-bold text-slate-900">Smart TV Samsung 65"</td>
                                <td className="px-6 py-4 text-xs font-bold text-slate-600">Cetrogar</td>
                                <td className="px-6 py-4 text-xs font-black text-emerald-600">-45%</td>
                                <td className="px-6 py-4">
                                    <span className="bg-emerald-50 text-emerald-600 px-2 py-1 rounded text-[9px] font-black uppercase tracking-tighter">Liquidado</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    );
}
