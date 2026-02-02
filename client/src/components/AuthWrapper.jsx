import React, { createContext, useContext, useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar sesión al cargar la app
    const savedSession = localStorage.getItem('oxxo_session');
    if (savedSession) {
      try {
        // En un entorno real, aquí validaríamos el token con el servidor
        setUser(JSON.parse(savedSession));
      } catch (e) {
        localStorage.removeItem('oxxo_session');
      }
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    setUser(userData);
    // Almacenamos datos básicos (en producción usaríamos un JWT)
    localStorage.setItem('oxxo_session', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('oxxo_session');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

/**
 * AuthWrapper: Protege rutas según autenticación y roles
 */
const AuthWrapper = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-vps flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-oxxo-red"></div>
      </div>
    );
  }

  // 1. Verificar si hay sesión activa
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 2. Verificar permisos de rol (si se especifican)
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    console.warn(`Acceso denegado: El rol ${user.role} no tiene permiso para esta ruta.`);
    
    // Redirigir según el rol que tenga
    if (user.role === 'COLABORADOR') return <Navigate to="/register" replace />;
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default AuthWrapper;




