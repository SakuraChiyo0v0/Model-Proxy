import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Providers from './pages/Providers';
import RoutesPage from './pages/RoutesPage';
import Logs from './pages/Logs';

const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('admin_token'));

  const login = (t) => {
    localStorage.setItem('admin_token', t);
    setToken(t);
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function ProtectedRoute({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function Sidebar() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const links = [
    { path: '/dashboard', label: '概览', icon: '◫' },
    { path: '/providers', label: '模型厂商', icon: '◫' },
    { path: '/routes', label: '路由管理', icon: '◫' },
    { path: '/logs', label: '请求日志', icon: '◫' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-logo">Model Proxy</div>
      <nav className="sidebar-nav">
        {links.map((link) => (
          <button
            key={link.path}
            className={`sidebar-link ${location.pathname === link.path ? 'active' : ''}`}
            onClick={() => navigate(link.path)}
          >
            <span>{link.icon}</span>
            <span>{link.label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <button className="logout-btn" onClick={logout}>
          <span>←</span>
          <span>退出登录</span>
        </button>
      </div>
    </div>
  );
}

function Layout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">{children}</div>
    </div>
  );
}

function Toast({ message, type, key }) {
  return (
    <div key={key} className={`toast toast-${type}`}>
      {message}
    </div>
  );
}

export default function App() {
  const [toast, setToast] = useState(null);
  const [toastKey, setToastKey] = useState(0);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setToastKey((k) => k + 1);
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    document.title = 'Model Proxy';
  }, []);

  return (
    <AuthProvider>
      <BrowserRouter>
        {toast && <Toast key={toastKey} message={toast.message} type={toast.type} />}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout><Dashboard showToast={showToast} /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/providers"
            element={
              <ProtectedRoute>
                <Layout><Providers showToast={showToast} /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/routes"
            element={
              <ProtectedRoute>
                <Layout><RoutesPage showToast={showToast} /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs"
            element={
              <ProtectedRoute>
                <Layout><Logs showToast={showToast} /></Layout>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
