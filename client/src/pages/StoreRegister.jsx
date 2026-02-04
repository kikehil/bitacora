import React, { useState } from 'react';

const StoreRegister = ({ user }) => {
  const [formData, setFormData] = useState({
    amount: '',
    collaborator2: '',
    passwordCollab2: '',
    photo: null,
    photoPreview: null
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({
        ...formData,
        photo: file,
        photoPreview: URL.createObjectURL(file)
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulación de envío al servidor
    const data = new FormData();
    data.append('cr', user.cr);
    data.append('amount', formData.amount);
    data.append('collaborator1', user.username);
    data.append('collaborator2', formData.collaborator2);
    data.append('photo', formData.photo);
    data.append('date', new Date().toISOString().split('T')[0]);
    data.append('time', new Date().toTimeString().split(' ')[0].slice(0, 5));

    try {
      const response = await fetch('http://localhost:5000/api/withdrawals', {
        method: 'POST',
        body: data,
      });
      
      if (response.ok) {
        setShowSuccess(true);
        setFormData({ amount: '', collaborator2: '', passwordCollab2: '', photo: null, photoPreview: null });
        setTimeout(() => setShowSuccess(false), 3000);
      }
    } catch (error) {
      alert('Error al registrar el retiro');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4 space-y-6 font-sans">
      {/* Header Móvil */}
      <div className="text-center space-y-1">
        <h2 className="text-2xl font-black text-gray-800 uppercase italic">Nuevo Retiro</h2>
        <p className="text-xs font-bold text-red-600 bg-red-50 inline-block px-3 py-1 rounded-full">
          TIENDA: {user.cr}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Campo Monto */}
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Monto del Retiro</label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-2xl font-bold text-gray-400">$</span>
            <input
              type="number"
              inputMode="decimal"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({...formData, amount: e.target.value})}
              className="w-full pl-10 pr-4 py-4 text-3xl font-black text-red-600 focus:outline-none rounded-xl bg-gray-50 border-2 border-transparent focus:border-yellow-400 transition"
              placeholder="0.00"
              required
            />
          </div>
        </div>

        {/* Validación Dual */}
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 space-y-4">
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest">Autorización Segundo Colaborador</label>
          </div>
          
          <input
            type="text"
            placeholder="Usuario del Colaborador 2"
            value={formData.collaborator2}
            onChange={(e) => setFormData({...formData, collaborator2: e.target.value})}
            className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm font-bold focus:border-red-500 outline-none"
            required
          />
          <input
            type="password"
            placeholder="PIN / Contraseña"
            value={formData.passwordCollab2}
            onChange={(e) => setFormData({...formData, passwordCollab2: e.target.value})}
            className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm font-bold focus:border-red-500 outline-none"
            required
          />
        </div>

        {/* Captura de Foto */}
        <div className="space-y-3">
          <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest text-center">Evidencia de Fajilla</label>
          <div className="relative group">
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handlePhotoChange}
              className="hidden"
              id="photo-upload"
              required={!formData.photoPreview}
            />
            <label
              htmlFor="photo-upload"
              className={`flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-2xl cursor-pointer transition-all ${
                formData.photoPreview ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
              }`}
            >
              {formData.photoPreview ? (
                <img src={formData.photoPreview} alt="Preview" className="w-full h-full object-cover rounded-2xl" />
              ) : (
                <div className="text-center space-y-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <p className="text-xs font-black text-gray-500 uppercase">Tocar para tomar foto</p>
                </div>
              )}
            </label>
          </div>
        </div>

        {/* Botón Guardar */}
        <button
          type="submit"
          disabled={isSubmitting}
          className={`w-full py-4 rounded-2xl font-black text-white shadow-xl transition transform active:scale-95 ${
            isSubmitting ? 'bg-gray-400' : 'bg-red-600 hover:bg-red-700 shadow-red-200'
          }`}
        >
          {isSubmitting ? 'PROCESANDO...' : 'GUARDAR RETIRO'}
        </button>
      </form>

      {/* Animación de Éxito */}
      {showSuccess && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-white bg-opacity-90 animate-in fade-in duration-300">
          <div className="text-center space-y-4 scale-in-center">
            <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto shadow-lg shadow-green-200">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-xl font-black text-gray-800 uppercase italic">¡Registro Exitoso!</h3>
            <p className="text-xs font-bold text-gray-500">El retiro ha sido guardado correctamente.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreRegister;





