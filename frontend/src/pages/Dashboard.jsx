import React, { useState, useEffect } from 'react';
import api from '../api';

export default function Dashboard({ showToast }) {
  const [providers, setProviders] = useState([]);
  const [logs, setLogs] = useState({ total: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/admin/providers'),
      api.get('/api/admin/logs?limit=1'),
    ])
      .then(([p, l]) => {
        setProviders(p.data);
        setLogs(l.data);
      })
      .catch(() => showToast('加载概览数据失败', 'error'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ padding: 32, color: 'var(--text-muted)' }}>加载中...</div>;

  const active = providers.filter(p => p.enabled);

  return (
    <>
      <h1 className="page-title">概览</h1>
      <p className="page-subtitle">Model Proxy 运行状态</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
        <StatCard label="模型厂商" value={providers.length} sub={`${active.length} 个已启用`} />
        <StatCard label="已配置 Key" value={active.filter(p=>p.has_key).length} sub="个厂商" />
        <StatCard label="请求日志" value={logs.total || 0} sub="累计请求数" />
      </div>

      <div style={{ padding: 24, background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 8 }}>
        <h3 style={{ fontSize: 16, marginBottom: 16 }}>快速开始</h3>
        <div style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.8 }}>
          <p>1. 在 <strong>模型厂商</strong> 中选择模板，填写 API Key</p>
          <p>2. 发送请求到 <code style={{ background: 'var(--bg-tertiary)', padding: '2px 6px', borderRadius: 4, fontSize: 13 }}>POST /v1/chat/completions</code></p>
          <p>3. 请求中 <code style={{ background: 'var(--bg-tertiary)', padding: '2px 6px', borderRadius: 4, fontSize: 13 }}>"model"</code> 字段自动匹配厂商</p>
        </div>
      </div>
    </>
  );
}

function StatCard({ label, value, sub }) {
  return (
    <div style={{ padding: 20, background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 8 }}>
      <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 600, marginBottom: 4 }}>{value}</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{sub}</div>
    </div>
  );
}
