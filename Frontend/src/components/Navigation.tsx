import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navigation: React.FC = () => {
  const { user, signOut } = useAuth();

  return (
    <header className="sticky top-0 z-50 w-full bg-white/80 border-b border-line-soft backdrop-blur-sm">
      <div className="container h-16 flex items-center justify-between">
        <Link to="/" className="text-h3 font-bold text-gray-900">
          NewsBite
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          <NavLink to="/dashboard" className={({ isActive }) => 
            `text-body font-medium ${isActive ? 'text-brand-primary' : 'text-gray-800 hover:text-brand-primary'}`
          }>
            대시보드
          </NavLink>
          <NavLink to="/preferences" className={({ isActive }) => 
            `text-body font-medium ${isActive ? 'text-brand-primary' : 'text-gray-800 hover:text-brand-primary'}`
          }>
            관심사 설정
          </NavLink>
        </nav>

        <div>
          {user ? (
            <div className="flex items-center gap-4">
              <span className="hidden sm:inline text-caption text-gray-600">{user.email}</span>
              <button
                onClick={signOut}
                className="btn btn-secondary btn-sm"
              >
                로그아웃
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn btn-primary btn-md">
              시작하기
            </Link>
          )})
        </div>
      </div>
    </header>
  );
};

export default Navigation;