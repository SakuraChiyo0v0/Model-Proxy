import React, { useState, useEffect } from 'react';
import api from '../api';

export default function RoutesPage({ showToast }) {
  const [routes, setRoutes] = useState([]);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modal
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({ alias: '', provider_id: '', api_key: '', model: '' });

  // 模型列表
  const [models, setModels] = useState([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [modelsError, setModelsError] = useState(false);

  const fetchData = async () => {
    try {
      const [rRes, pRes] = await Promise.all([
        api.get('/api/admin/routes'),
        api.get('/api/admin/providers'),
      ]);
      setRoutes(rRes.data);
      setProviders(pRes.data.filter(p => p.enabled));
    } catch (e) {
      showToast('加载失败', 'error');
    }
  };

  useEffect(() => { fetchData(); }, []);

  // 选厂商后自动拉取模型列表
  const fetchModels = async (providerId) => {
    if (!providerId) {
      setModels([]);
      setModelsError(false);
      return;
    }
    setModelsLoading(true);
    setModelsError(false);
    try {
      const res = await api.get(`/api/admin/providers/${providerId}/models`);
      if (res.data.models && res.data.models.length > 0) {
        setModels(res.data.models);
        setModelsError(false);
      } else {
        setModels([]);
        setModelsError(true); // 不支持，切换为手动输入
      }
    } catch (e) {
      setModels([]);
      setModelsError(true);
    }
    setModelsLoading(false);
  };

  const openAdd = () => {
    setForm({ alias: '', provider_id: '', api_key: '', model: '' });
    setModels([]);
    setModelsError(false);
    setEditId(null);
    setShowModal(true);
  };

  const openEdit = (r) => {
    setForm({ alias: r.alias, provider_id: r.provider_id, api_key: r.api_key, model: r.model || '' });
    setEditId(r.id);
    setShowModal(true);
    // 拉取对应厂商的模型列表
    fetchModels(r.provider_id);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditId(null);
  };

  const handleProviderChange = (e) => {
    const pid = e.target.value;
    setForm({ ...form, provider_id: pid, model: '' });
    fetchModels(pid);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.alias.trim() || !form.provider_id || !form.api_key.trim()) {
      showToast('请填写完整', 'error');
      return;
    }
    if (!form.model.trim()) {
      showToast('请选择或输入模型', 'error');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        ...form,
        provider_id: Number(form.provider_id),
      };
      if (editId) {
        if (!payload.api_key) delete payload.api_key;
        await api.put(`/api/admin/routes/${editId}`, payload);
        showToast('已更新');
      } else {
        await api.post('/api/admin/routes', payload);
        showToast('已创建');
      }
      closeModal();
      fetchData();
    } catch (e) {
      showToast(e.response?.data?.detail || '操作失败', 'error');
    }
    setLoading(false);
  };

  const handleToggle = async (r) => {
    try {
      await api.put(`/api/admin/routes/${r.id}`, { enabled: !r.enabled });
      fetchData();
    } catch (e) {
      showToast('操作失败', 'error');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('确定删除？')) return;
    try {
      await api.delete(`/api/admin/routes/${id}`);
      showToast('已删除');
      fetchData();
    } catch (e) {
      showToast('删除失败', 'error');
    }
  };

  const getProvider = (pid) => providers.find(x => x.id === pid);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">API Key 管理</h1>
          <p className="page-subtitle">自定义代理 Key → 绑定厂商 + 模型，标准接口统一访问</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={openAdd}>+ 添加 Key</button>
      </div>

      {routes.length === 0 ? (
        <div className="empty-state">
          <h3>暂无自定义 API Key</h3>
          <button className="btn btn-primary btn-sm" onClick={openAdd}>+ 添加 Key</button>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>名称</th>
                <th>绑定厂商</th>
                <th>模型</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {routes.map(r => {
                const p = getProvider(r.provider_id);
                return (
                  <tr key={r.id}>
                    <td>
                      <code style={{ fontWeight: 'bold' }}>{r.alias}</code>
                    </td>
                    <td>{p ? p.label : `厂商 #${r.provider_id}`}</td>
                    <td>
                      <code style={{ fontSize: 13 }}>{r.model || '-'}</code>
                    </td>
                    <td>
                      <span style={{ cursor: 'pointer' }} onClick={() => handleToggle(r)}>
                        <span className={`badge ${r.enabled ? 'badge-success' : 'badge-muted'}`}>
                          {r.enabled ? '启用中' : '已禁用'}
                        </span>
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-outline btn-sm" onClick={() => openEdit(r)}>编辑</button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(r.id)}>删除</button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ marginTop: 16, fontSize: 13, color: 'var(--text-muted)' }}>
        <p>使用方式：将这里的 Key 填入客户端 <code>API Key</code> 字段，<code>API Base</code> 设为 <code>{window.location.origin}</code>，请求时自动使用绑定的模型，无需再传 model 字段。</p>
      </div>

      {/* ── Add / Edit Modal ── */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>{editId ? '编辑 API Key' : '添加 API Key'}</h2>
            <div className="modal-body">
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">名称</label>
                  <input
                    className="form-input"
                    value={form.alias}
                    onChange={e => setForm({ ...form, alias: e.target.value })}
                    placeholder="例如：我的OpenAI"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">绑定厂商</label>
                  <select
                    className="form-select"
                    value={form.provider_id}
                    onChange={handleProviderChange}
                    required
                  >
                    <option value="">-- 选择厂商 --</option>
                    {providers.map(p => (
                      <option key={p.id} value={p.id}>{p.label} ({p.base_url})</option>
                    ))}
                  </select>
                </div>

                {/* 模型选择 / 手动输入 */}
                {form.provider_id && (
                  <div className="form-group">
                    <label className="form-label">绑定模型</label>
                    {modelsLoading ? (
                      <div style={{ fontSize: 13, color: 'var(--text-muted)', padding: '8px 0' }}>
                        正在获取模型列表...
                      </div>
                    ) : models.length > 0 ? (
                      <select
                        className="form-select"
                        value={form.model}
                        onChange={e => setForm({ ...form, model: e.target.value })}
                        required
                      >
                        <option value="">-- 选择模型 --</option>
                        {models.map(m => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    ) : (
                      <>
                        <input
                          className="form-input"
                          value={form.model}
                          onChange={e => setForm({ ...form, model: e.target.value })}
                          placeholder={modelsError ? '该厂商不支持自动获取，请手动输入模型名' : '输入模型名'}
                          required
                        />
                        {modelsError && (
                          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                            该厂商暂不支持自动获取模型列表，请手动输入
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label">自定义 API Key</label>
                  <input
                    className="form-input"
                    type="text"
                    value={form.api_key}
                    onChange={e => setForm({ ...form, api_key: e.target.value })}
                    placeholder={editId ? '留空不修改' : '输入代理 Key'}
                    required={!editId}
                  />
                </div>

                <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
                  <button className="btn btn-primary" type="submit" disabled={loading}>
                    {editId ? '保存修改' : '确认添加'}
                  </button>
                  <button className="btn btn-outline" type="button" onClick={closeModal}>
                    取消
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
