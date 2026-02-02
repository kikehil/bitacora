import React, { useState } from 'react';

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email, password }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        onLogin(data.user);
      } else {
        setError(data.message || 'Credenciales incorrectas');
      }
    } catch (err) {
      setError('Error de conexión con el servidor');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-vps relative overflow-hidden font-sans">
      {/* Círculos de luz de fondo para el efecto de profundidad */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-oxxo-red opacity-10 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-oxxo-red opacity-10 blur-[120px] rounded-full"></div>

      <div className="max-w-md w-full z-10 px-6">
        {/* Contenedor con Glassmorphism */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-10 rounded-3xl shadow-2xl">
          <div className="text-center mb-10">
            <div className="inline-block mb-6">
              <div className="bg-oxxo-red text-white px-6 py-2 rounded-md font-black text-4xl italic shadow-glow-red">
                OXXO
              </div>
            </div>
            <h2 className="text-xl font-black text-white uppercase tracking-[0.2em]">Bitácora Digital</h2>
            <div className="h-1 w-12 bg-oxxo-yellow mx-auto mt-2 rounded-full"></div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-200 text-xs font-bold uppercase text-center animate-pulse">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2 ml-1">Correo Electrónico</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="vps-input w-full bg-black/40 backdrop-blur-md border-white/10 focus:border-oxxo-yellow transition-all"
                placeholder="usuario@oxxo.com"
                required
              />
            </div>
            
            <div>
              <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2 ml-1">Contraseña</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="vps-input w-full bg-black/40 backdrop-blur-md border-white/10 focus:border-oxxo-yellow transition-all"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 bg-oxxo-red hover:bg-oxxo-yellow text-white hover:text-black font-black rounded-xl shadow-lg hover:shadow-glow-yellow transition-all duration-300 active:scale-95 uppercase tracking-widest"
            >
              {isLoading ? 'Cargando...' : 'Entrar'}
            </button>
          </form>
        </div>
        
        <footer className="text-center mt-10">
          <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.3em]">
            Bitácora Digital OXXO - Control de Valores v1.0
          </p>
        </footer>
      </div>
    </div>
  );
};

export default LoginPage;
