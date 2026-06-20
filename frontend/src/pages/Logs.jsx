import React, { useState, useEffect } from 'react';
import api from '../api';

export default function Logs({ showToast }) {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState(null);
  const limit = 20;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/admin/logs?skip=${page * limit}&limit=${limit}`);
      setLogs(res.data.items);
      setTotal(res.data.total);
    } catch {
      showToast('加载失败', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [page]);

  const openDetail = async (id) => {
    try {
      const res = await api.get(`/api/admin/logs/${id}`);
      setDetail(res.data);
    } catch {
      showToast('加载详情失败', 'error');
    }
  };

  const totalPages = Math.ceil(total / limit);

  const formatBody = (body) => {
    if (!body) return '-';
    try {
      return JSON.stringify(JSON.parse(body), null, 2);
    } catch {
      return body;
    }
  };

  return (
    <>
      <h1 className="page-title">请求日志</h1>
      <p className="page-subtitle">共 {total} 条请求记录</p>

      {loading ? (
        <div style={{ color: 'var(--text-muted)' }}>加载中...</div>
      ) : logs.length === 0 ? (
        <div className="empty-state">
          <h3>暂无日志</h3>
          <p>未有代理请求</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>时间</th>
                  <th>模型</th>
                  <th>状态</th>
                  <th>Token</th>
                  <th>延迟</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ fontSize: 13, color: 'var(--text-muted)' }}>{log.created_at}</td>
                    <td style={{ fontSize: 13 }}>{log.model || '-'}</td>
                    <td>
                      <span className={`badge ${log.status_code === 200 ? 'badge-success' : 'badge-danger'}`}>
                        {log.status_code}
                      </span>
                    </td>
                    <td style={{ fontSize: 13, color: 'var(--accent)' }}>{log.tokens_used ?? '-'}</td>
                    <td style={{ fontSize: 13, color: 'var(--text-muted)' }}>{log.latency_ms != null ? `${log.latency_ms}ms` : '-'}</td>
                    <td>
                      <button className="btn btn-outline btn-sm" onClick={() => openDetail(log.id)}>详情</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button className="btn btn-outline btn-sm" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}>
                上一页
              </button>
              <span style={{ fontSize: 13, color: 'var(--text-muted)', padding: '0 12px' }}>
                {page + 1} / {totalPages}
              </span>
              <button className="btn btn-outline btn-sm" onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1}>
                下一页
              </button>
            </div>
          )}
        </>
      )}

      {detail && (
        <div className="modal-overlay" onClick={() => setDetail(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>日志详情</h2>
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 16, fontSize: 13 }}>
                <div><span style={{ color: 'var(--text-muted)' }}>模型：</span>{detail.model || '-'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>状态：</span>{detail.status_code}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>Token：</span>{detail.tokens_used ?? '-'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>延迟：</span>{detail.latency_ms}ms</div>
                <div><span style={{ color: 'var(--text-muted)' }}>时间：</span>{detail.created_at}</div>
                {detail.error_message && (
                  <div style={{ gridColumn: '1 / -1', color: 'var(--danger)' }}>
                    <span style={{ color: 'var(--text-muted)' }}>错误：</span>{detail.error_message}
                  </div>
                )}
              </div>

              <h4 style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>请求体</h4>
              <pre>{formatBody(detail.request_body)}</pre>

              <h4 style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>响应体</h4>
              <pre>{formatBody(detail.response_body)}</pre>
            </div>
            <div className="modal-actions">
              <button className="btn btn-outline btn-sm" onClick={() => setDetail(null)}>关闭</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
