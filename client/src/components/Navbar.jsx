import React from 'react';

const Navbar = ({ user, onLogout }) => {
  return (
    <nav className="bg-white shadow-md border-b-2 border-yellow-400 px-6 py-3 flex justify-between items-center">
      <div className="flex items-center space-x-3">
        <div className="bg-red-600 text-white px-3 py-1 rounded font-black text-xl italic">OXXO</div>
        <div className="h-6 w-px bg-gray-300 mx-2"></div>
        <span className="text-gray-800 font-bold uppercase tracking-tight text-sm md:text-base">Bitácora Digital</span>
      </div>
      
      <div className="flex items-center space-x-6">
        <div className="hidden md:flex flex-col items-end">
          <span className="text-gray-900 font-extrabold text-sm leading-none">{user.name}</span>
          <span className="text-red-600 font-bold text-[10px] uppercase tracking-tighter">{user.role}</span>
        </div>
        <button
          onClick={onLogout}
          className="flex items-center space-x-2 bg-gray-100 hover:bg-red-50 text-gray-600 hover:text-red-600 px-4 py-2 rounded-lg font-bold text-xs transition duration-200 border border-gray-200 hover:border-red-200"
        >
          <span>SALIR</span>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;




