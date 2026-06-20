import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../App';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/api/admin/login', { username, password });
      login(res.data.token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Model Proxy</h1>
        <p>登录管理后台</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">用户名</label>
            <input
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="输入用户名"
              autoFocus
            />
          </div>
          <div className="form-group">
            <label className="form-label">密码</label>
            <input
              className="form-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="输入密码"
            />
          </div>
          {error && <p style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 14 }}>{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? '登录中...' : '登录'}
          </button>
        </form>
      </div>
    </div>
  );
}
