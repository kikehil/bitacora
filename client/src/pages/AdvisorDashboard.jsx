import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';

const AdvisorDashboard = ({ user, onLogout }) => {
  const [stores, setStores] = useState([]);
  const [stats, setStats] = useState({ total_stores: 0, today_amount: 0 });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStore, setSelectedStore] = useState(null);
  const [storeHistory, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInitialData();
  }, [user.username]);

  const fetchInitialData = async () => {
    try {
      const [storesRes, statsRes] = await Promise.all([
        fetch(`http://localhost:5000/api/advisor/stores/${user.username}`),
        fetch(`http://localhost:5000/api/advisor/stats/${user.username}`)
      ]);
      const storesData = await storesRes.json();
      const statsData = await statsRes.json();
      setStores(storesData);
      setStats(statsData);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  const fetchStoreHistory = async (store) => {
    setSelectedStore(store);
    try {
      const res = await fetch(`http://localhost:5000/api/withdrawals/${store.cr}`);
      const data = await res.json();
      setHistory(data);
    } catch (error) {
      console.error('Error loading store history:', error);
    }
  };

  const filteredStores = stores.filter(s => 
    s.cr.toLowerCase().includes(searchTerm.toLowerCase()) || 
    s.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const exportReport = () => {
    const reportData = storeHistory.length > 0 ? storeHistory : withdrawals;
    
    // Si no hay historial cargado de una tienda específica, usamos todos los retiros del asesor
    const dataToExport = reportData.map(w => ({
      'Fecha': w.date,
      'Hora': w.time,
      'CR': w.cr,
      'Monto': w.amount,
      'Registró': w.collaborator1,
      'Validó': w.collaborator2
    }));

    const ws = XLSX.utils.json_to_sheet(dataToExport);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Reporte de Plaza");
    XLSX.writeFile(wb, `Reporte_Plaza_${user.username}_${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  if (loading) return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
      <div className="w-12 h-12 border-4 border-oxxo-red border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100 font-sans p-6">
      {/* Header VPS */}
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-10 bg-[#161616]/50 backdrop-blur-md p-4 rounded-2xl border border-white/5 shadow-2xl">
        <div className="flex items-center space-x-4">
          <div className="bg-oxxo-red text-white px-4 py-1 rounded font-black italic text-xl shadow-glow-red">OXXO</div>
          <div>
            <h1 className="text-sm font-black uppercase tracking-[0.2em]">Centro de Mando</h1>
            <p className="text-[9px] text-gray-500 font-bold uppercase tracking-widest">Asesor: {user.name}</p>
          </div>
        </div>
        <div className="flex items-center space-x-6">
          <button 
            onClick={exportReport}
            className="bg-[#161616] border border-oxxo-red/50 text-[10px] font-black text-gray-300 hover:text-white hover:border-oxxo-red px-4 py-2 rounded-lg transition-all uppercase tracking-widest flex items-center space-x-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Exportar Reporte de Plaza</span>
          </button>
          <button onClick={onLogout} className="text-[10px] font-black text-gray-500 hover:text-oxxo-red transition-colors uppercase tracking-widest">Desconectar Terminal ➔</button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-10">
        {/* KPIs Superiores */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl shadow-vps relative overflow-hidden group hover:border-oxxo-red/30 transition-all">
            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Tiendas a cargo</p>
            <h3 className="text-4xl font-black text-white tracking-tighter">{stats.total_stores}</h3>
            <div className="absolute -right-4 -bottom-4 text-white/5 text-6xl font-black italic group-hover:text-oxxo-red/10 transition-colors">CRs</div>
          </div>

          <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl shadow-vps relative overflow-hidden group hover:border-oxxo-yellow/30 transition-all">
            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Monto Total Hoy</p>
            <h3 className="text-4xl font-black text-white tracking-tighter font-mono-tech">${stats.today_amount.toLocaleString('es-MX')}</h3>
            <div className="absolute -right-4 -bottom-4 text-white/5 text-6xl font-black italic group-hover:text-oxxo-yellow/10 transition-colors">MXN</div>
          </div>

          <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl shadow-vps flex items-center justify-between">
            <div>
              <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Estatus Operativo</p>
              <h3 className="text-xl font-black text-green-500 uppercase italic tracking-tighter">Sincronizado</h3>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse shadow-[0_0_15px_rgba(34,197,94,0.8)] mb-1"></div>
              <span className="text-[8px] font-black text-green-500/50 uppercase">Live</span>
            </div>
          </div>
        </div>

        {/* Buscador Inteligente */}
        <div className="relative group">
          <input 
            type="text"
            placeholder="Filtrar por CR o Nombre de Tienda..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#161616] border border-gray-800 rounded-2xl px-12 py-5 text-lg font-bold focus:border-oxxo-red focus:shadow-glow-red outline-none transition-all placeholder-gray-700"
          />
          <svg className="h-6 w-6 absolute left-4 top-1/2 -translate-y-1/2 text-gray-600 group-focus-within:text-oxxo-red transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* Grilla de Tiendas */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredStores.map(store => (
            <div 
              key={store.cr} 
              onClick={() => fetchStoreHistory(store)}
              className="bg-[#161616] border border-gray-800 p-5 rounded-2xl hover:border-oxxo-yellow/50 hover:shadow-glow-yellow cursor-pointer transition-all group relative overflow-hidden"
            >
              <div className="flex justify-between items-start mb-4">
                <span className="text-oxxo-yellow font-black text-xl tracking-tighter">{store.cr}</span>
                <div className="w-2 h-2 bg-gray-800 rounded-full group-hover:bg-oxxo-yellow transition-colors"></div>
              </div>
              <h4 className="text-white font-bold text-sm uppercase leading-tight h-10 overflow-hidden group-hover:text-oxxo-yellow transition-colors">{store.name}</h4>
              <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between items-center">
                <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest">Terminal ID</span>
                <span className="text-[9px] font-black text-oxxo-red uppercase">Ver Historial ➔</span>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Sidebar Detalle de Retiros */}
      {selectedStore && (
        <div className="fixed inset-0 z-[100] flex justify-end animate-in fade-in duration-300">
          <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setSelectedStore(null)}></div>
          <div className="relative w-full max-w-2xl bg-[#0d0d0d] border-l border-gray-800 shadow-2xl h-full flex flex-col animate-in slide-in-from-right duration-500">
            <div className="p-8 border-b border-gray-800 flex justify-between items-center bg-[#161616]/50">
              <div>
                <h2 className="text-2xl font-black text-white uppercase italic tracking-tighter">{selectedStore.name}</h2>
                <p className="text-xs text-oxxo-yellow font-bold uppercase tracking-widest">Historial de Operaciones • {selectedStore.cr}</p>
              </div>
              <button onClick={() => setSelectedStore(null)} className="p-2 hover:bg-red-500/10 rounded-full text-gray-500 hover:text-oxxo-red transition-all">
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-6">
              {storeHistory.length > 0 ? (
                <div className="space-y-4">
                  {storeHistory.map(h => (
                    <div key={h.id} className="bg-[#161616] border border-gray-800 p-6 rounded-2xl flex justify-between items-center group hover:border-oxxo-red/30 transition-all">
                      <div className="space-y-1">
                        <p className="text-3xl font-black text-white font-mono-tech">${h.amount.toLocaleString()}</p>
                        <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">{h.date} • {h.time}</p>
                        <div className="flex space-x-4 mt-2">
                          <div>
                            <p className="text-[8px] text-gray-600 font-black uppercase">Registró</p>
                            <p className="text-[10px] text-gray-400 font-bold">{h.collaborator1}</p>
                          </div>
                          <div>
                            <p className="text-[8px] text-gray-600 font-black uppercase">Validó</p>
                            <p className="text-[10px] text-gray-400 font-bold">{h.collaborator2}</p>
                          </div>
                        </div>
                      </div>
                      {h.photo_url && (
                        <button 
                          onClick={() => window.open(`http://localhost:5000${h.photo_url}`, '_blank')}
                          className="bg-oxxo-red/10 hover:bg-oxxo-red text-oxxo-red hover:text-white p-4 rounded-xl border border-oxxo-red/20 transition-all group-hover:shadow-glow-red"
                        >
                          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-20">
                  <div className="text-6xl">📊</div>
                  <p className="text-xl font-black uppercase italic tracking-widest text-white">Sin registros hoy</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvisorDashboard;
