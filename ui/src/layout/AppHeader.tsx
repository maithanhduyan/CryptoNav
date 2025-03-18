// src/layout/AppHeader.tsx
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function AppHeader() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    signOut();
    navigate('/signin');
  };

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-4 py-3 flex justify-between items-center">
      <h1 className="text-white font-semibold text-xl">CryptoNav</h1>
      <div className="flex items-center space-x-4">
        <span className="text-gray-400">Hi, {user?.username}</span>
        <button onClick={handleLogout} className="text-gray-300 hover:text-white">
          Sign out
        </button>
      </div>
    </header>
  );
}
