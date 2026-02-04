import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';

const WithdrawalForm = ({ user, onBack }) => {
  const [amount, setAmount] = useState('');
  const [photo, setPhoto] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [successData, setSuccessData] = useState(null);
  const [error, setError] = useState('');

  const webcamRef = useRef(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setPhoto(imageSrc);
  }, [webcamRef]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!photo) {
      setError('La evidencia fotográfica es obligatoria');
      return;
    }

    setIsUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('cr', user.cr);
    formData.append('amount', amount);
    formData.append('collaborator1', user.username);
    
    const fetchRes = await fetch(photo);
    const blob = await fetchRes.blob();
    formData.append('photo', blob, `${user.cr}_evidence.jpg`);

    try {
      const response = await fetch('http://localhost:5000/api/withdrawals', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      
      if (data.success) {
        setSuccessData(data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Error de conexión con el servidor VPS');
    } finally {
      setIsUploading(false);
    }
  };

  if (successData) {
    return (
      <div className="max-w-md mx-auto p-8 animate-in zoom-in-95 duration-500">
        <div className="vps-card p-8 border-t-4 border-green-500 text-center space-y-6 shadow-glow-green">
          <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
            <svg className="h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-black text-white uppercase italic">{successData.message}</h2>
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Folio de Operación</p>
            <p className="text-2xl font-mono text-oxxo-yellow">{successData.folio}</p>
          </div>
          <button onClick={onBack} className="btn-oxxo w-full py-3 text-xs">Volver al Inicio</button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto p-6 font-sans space-y-8">
      <div className="vps-card p-8 border-t-4 border-oxxo-red relative overflow-hidden">
        {isUploading && (
          <div className="absolute inset-0 bg-black/80 z-50 flex flex-col items-center justify-center space-y-4 backdrop-blur-sm">
            <div className="w-12 h-12 border-4 border-oxxo-red border-t-transparent rounded-full animate-spin"></div>
            <p className="text-[10px] font-black text-oxxo-red uppercase tracking-[0.3em] animate-pulse">Sincronizando con VPS...</p>
          </div>
        )}

        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-2xl font-black text-white uppercase italic tracking-tighter">Registro Directo</h2>
            <p className="text-[10px] text-oxxo-yellow font-bold uppercase tracking-widest">Tienda: {user.cr}</p>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-gray-500 font-bold uppercase">Terminal</p>
            <p className="text-xs font-black text-white">ONLINE</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* MONTO */}
          <div className="bg-black/40 p-6 rounded-2xl border border-gray-800 focus-within:border-oxxo-red transition-all">
            <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Monto del Retiro</label>
            <div className="flex items-center">
              <span className="text-4xl font-black text-oxxo-yellow mr-3">$</span>
              <input 
                type="number" 
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="bg-transparent text-5xl font-mono text-white w-full focus:outline-none placeholder-gray-800"
                placeholder="0.00"
                required
              />
            </div>
          </div>

          {/* EVIDENCIA FOTOGRÁFICA */}
          <div className="space-y-4">
            <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Evidencia Fotográfica Obligatoria</label>
            {!photo ? (
              <div className="relative rounded-2xl overflow-hidden border-2 border-dashed border-gray-800 group hover:border-oxxo-red transition-all">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full aspect-video object-cover"
                  videoConstraints={{ facingMode: "environment" }}
                />
                <button 
                  type="button"
                  onClick={capture}
                  className="absolute inset-0 flex flex-col items-center justify-center bg-black/20 group-hover:bg-black/0 transition-all"
                >
                  <div className="p-4 bg-oxxo-red rounded-full shadow-glow-red transform group-hover:scale-110 transition-transform">
                    <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <span className="mt-4 text-[10px] font-black text-white uppercase tracking-widest">Capturar Fajilla</span>
                </button>
              </div>
            ) : (
              <div className="relative rounded-2xl overflow-hidden border-2 border-oxxo-red shadow-glow-red animate-in fade-in duration-300">
                <img src={photo} alt="Evidencia" className="w-full aspect-video object-cover" />
                <button 
                  type="button"
                  onClick={() => setPhoto(null)}
                  className="absolute top-4 right-4 p-2 bg-black/60 hover:bg-oxxo-red text-white rounded-full transition-all"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
            )}
          </div>

          {error && <p className="text-center text-oxxo-red text-[10px] font-black uppercase animate-bounce">{error}</p>}

          <button 
            type="submit"
            disabled={isUploading || !amount || !photo}
            className={`btn-oxxo w-full py-5 text-sm tracking-[0.2em] ${(!amount || !photo) ? 'opacity-30 grayscale cursor-not-allowed' : 'shadow-glow-red'}`}
          >
            {isUploading ? 'SINCRONIZANDO...' : 'Finalizar Registro y Notificar'}
          </button>
        </form>
      </div>
      
      <button onClick={onBack} className="w-full text-[10px] font-bold text-gray-600 hover:text-white uppercase tracking-widest transition-colors text-center">
        ⬅ Cancelar y Volver
      </button>
    </div>
  );
};

export default WithdrawalForm;
