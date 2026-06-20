import React, { useState, useEffect } from 'react';
import api from '../api';

export default function Providers({ showToast }) {
  const [providers, setProviders] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  // Add modal
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ template_name: '', key_value: '' });
  const [templateDetail, setTemplateDetail] = useState(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  // Edit modal
  const [showEdit, setShowEdit] = useState(false);
  const [editProvider, setEditProvider] = useState(null);
  const [editForm, setEditForm] = useState({ label: '', base_url: '', api_path: '' });
  // Keys
  const [keys, setKeys] = useState({});
  const [showKeys, setShowKeys] = useState(null);
  const [newKeyValue, setNewKeyValue] = useState('');
  const [newKeyAlias, setNewKeyAlias] = useState('');
  const [newKeyResult, setNewKeyResult] = useState(null);
  // Key editing
  const [editKeyId, setEditKeyId] = useState(null);
  const [editKeyForm, setEditKeyForm] = useState({ alias: '', key_value: '' });
  // Balances
  const [balances, setBalances] = useState({});
  // Models
  const [models, setModels] = useState({});
  const [showModels, setShowModels] = useState(null);
  const [loadingModels, setLoadingModels] = useState(false);

  const fetchData = async () => {
    try {
      const [pr, tr] = await Promise.all([
        api.get('/api/admin/providers'),
        api.get('/api/admin/provider-templates'),
      ]);
      setProviders(pr.data);
      setTemplates(tr.data);
      pr.data.forEach(p => {
        if (p.enabled) fetchBalance(p.id);
      });
    } catch { showToast('加载失败', 'error'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const fetchBalance = async (id) => {
    try {
      const res = await api.get(`/api/admin/providers/${id}/balance`);
      if (res.data.balance) setBalances(b => ({ ...b, [id]: res.data.balance }));
    } catch {}
  };

  const fetchKeys = async (pid) => {
    try {
      const res = await api.get(`/api/admin/providers/${pid}/keys`);
      setKeys(k => ({ ...k, [pid]: res.data }));
      setShowKeys(pid);
    } catch { showToast('加载 Key 失败', 'error'); }
  };

  const fetchModels = async (pid) => {
    setLoadingModels(true);
    try {
      const res = await api.get(`/api/admin/providers/${pid}/models`);
      setModels(m => ({ ...m, [pid]: res.data.models || [] }));
      setShowModels(pid);
    } catch { showToast('加载模型列表失败', 'error'); }
    finally { setLoadingModels(false); }
  };

  // ── Add ──────────────────────────────────────

  const openAdd = () => {
    setForm({ template_name: '', key_value: '' });
    setTemplateDetail(null);
    setTestResult(null);
    setShowAdd(true);
  };

  const onSelectTemplate = async (name) => {
    setForm({ ...form, template_name: name });
    setTestResult(null);
    if (!name) { setTemplateDetail(null); return; }
    try {
      const res = await api.get(`/api/admin/provider-templates/${name}`);
      setTemplateDetail(res.data);
    } catch { setTemplateDetail(null); }
  };

  const handleTest = async () => {
    if (!form.template_name) { showToast('请先选择厂商', 'error'); return; }
    if (!form.key_value) { showToast('请先输入 API Key', 'error'); return; }
    setTesting(true); setTestResult(null);
    try {
      const res = await api.post('/api/admin/providers/test', form);
      setTestResult(res.data);
    } catch (err) {
      setTestResult({ ok: false, message: err.response?.data?.detail || '测试失败' });
    } finally { setTesting(false); }
  };

  const handleAdd = async () => {
    if (!form.template_name) { showToast('请选择厂商模板', 'error'); return; }
    if (!form.key_value) { showToast('请输入 API Key', 'error'); return; }
    try {
      await api.post('/api/admin/providers/from-template', form);
      showToast('厂商已创建');
      setShowAdd(false);
      fetchData();
    } catch (err) { showToast(err.response?.data?.detail || '创建失败', 'error'); }
  };

  // ── Edit ─────────────────────────────────────

  const openEdit = (p) => {
    setEditProvider(p);
    setEditForm({ label: p.label, base_url: p.base_url, api_path: p.api_path });
    setShowEdit(true);
  };

  const handleEdit = async () => {
    try {
      await api.put(`/api/admin/providers/${editProvider.id}`, editForm);
      showToast('已更新');
      setShowEdit(false);
      fetchData();
    } catch (err) { showToast(err.response?.data?.detail || '更新失败', 'error'); }
  };

  // ── Key management ───────────────────────────

  const handleAddKey = async (pid) => {
    if (!newKeyValue) return;
    try {
      const res = await api.post(`/api/admin/providers/${pid}/keys`, { key_value: newKeyValue, alias: newKeyAlias });
      setNewKeyResult(res.data.key_value);
      setNewKeyValue('');
      setNewKeyAlias('');
      fetchKeys(pid);
    } catch (err) { showToast(err.response?.data?.detail || '添加失败', 'error'); }
  };

  const startEditKey = (k) => {
    setEditKeyId(k.id);
    setEditKeyForm({ alias: k.alias, key_value: '' });
  };

  const cancelEditKey = () => {
    setEditKeyId(null);
    setEditKeyForm({ alias: '', key_value: '' });
  };

  const handleEditKey = async (pid, kid) => {
    try {
      const body = {};
      if (editKeyForm.alias !== undefined) body.alias = editKeyForm.alias;
      if (editKeyForm.key_value) body.key_value = editKeyForm.key_value;
      await api.put(`/api/admin/providers/${pid}/keys/${kid}`, body);
      showToast('Key 已更新');
      cancelEditKey();
      fetchKeys(pid);
    } catch (err) { showToast(err.response?.data?.detail || '更新失败', 'error'); }
  };

  const toggleKey = async (pid, kid, enabled) => {
    try { await api.put(`/api/admin/providers/${pid}/keys/${kid}`, { enabled: !enabled }); fetchKeys(pid); }
    catch { showToast('操作失败', 'error'); }
  };

  const handleDeleteKey = async (pid, kid) => {
    if (!window.confirm('确认删除？')) return;
    try { await api.delete(`/api/admin/providers/${pid}/keys/${kid}`); fetchKeys(pid); fetchData(); }
    catch (err) { showToast(err.response?.data?.detail || '删除失败', 'error'); }
  };

  // ── Common ───────────────────────────────────

  const toggleEnabled = async (p) => {
    try { await api.put(`/api/admin/providers/${p.id}`, { enabled: !p.enabled }); fetchData(); }
    catch { showToast('操作失败', 'error'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('确认删除？')) return;
    try { await api.delete(`/api/admin/providers/${id}`); showToast('已删除'); fetchData(); }
    catch { showToast('删除失败', 'error'); }
  };

  const formatBalance = (b) => {
    if (!b) return '-';
    const remain = Math.max(0, (b.total_balance ?? 0) - (b.total_used ?? 0));
    return `${remain.toFixed(2)} ${b.currency || ''}`;
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">模型厂商</h1>
          <p className="page-subtitle">选择模板、输入 Key、一步配置 | 支持多 Key | 可编辑 Key</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={openAdd}>+ 添加工商</button>
      </div>

      {loading ? (
        <div style={{ color: 'var(--text-muted)' }}>加载中...</div>
      ) : providers.length === 0 ? (
        <div className="empty-state">
          <h3>暂无厂商</h3>
          <button className="btn btn-primary btn-sm" onClick={openAdd}>+ 添加工商</button>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>厂商</th>
                <th>Key 数</th>
                <th>余额</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {providers.map((p) => (
                <React.Fragment key={p.id}>
                  <tr>
                    <td>
                      <div style={{ fontWeight: 500 }}>{p.label}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                        {p.base_url}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
                        {p.api_path}
                      </div>
                    </td>
                    <td>
                      <button className="btn-link" onClick={() => fetchKeys(p.id)}>
                        {p.key_count} 个
                      </button>
                    </td>
                    <td>
                      {balances[p.id] ? (
                        <span style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 500 }}>
                          {formatBalance(balances[p.id])}
                        </span>
                      ) : (
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>-</span>
                      )}
                    </td>
                    <td>
                      <span style={{ cursor: 'pointer' }} onClick={() => toggleEnabled(p)}>
                        <span className={`badge ${p.enabled ? 'badge-success' : 'badge-muted'}`}>
                          {p.enabled ? '已启用' : '已禁用'}
                        </span>
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-outline btn-sm" onClick={() => fetchModels(p.id)} disabled={loadingModels}>
                          {loadingModels && showModels === null ? '获取中...' : '模型'}
                        </button>
                        <button className="btn btn-outline btn-sm" onClick={() => openEdit(p)}>编辑</button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.id)}>删除</button>
                      </div>
                    </td>
                  </tr>
                  {/* Key list row */}
                  {showKeys === p.id && keys[p.id] && (
                    <tr key={`keys-${p.id}`}>
                      <td colSpan={5} style={{ padding: '8px 0' }}>
                        <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 12 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>API Keys</div>
                          {keys[p.id].map(k => (
                            <React.Fragment key={k.id}>
                              {editKeyId === k.id ? (
                                <div style={{ display: 'flex', gap: 8, padding: '6px 0', borderBottom: '1px solid var(--border)', alignItems: 'center' }}>
                                  <input className="form-input" style={{ width: 100 }} value={editKeyForm.alias}
                                    onChange={e => setEditKeyForm({ ...editKeyForm, alias: e.target.value })}
                                    placeholder="别名" />
                                  <input className="form-input" style={{ flex: 1 }} value={editKeyForm.key_value}
                                    onChange={e => setEditKeyForm({ ...editKeyForm, key_value: e.target.value })}
                                    placeholder="输入新 Key（留空不修改）" />
                                  <button className="btn btn-primary btn-sm" onClick={() => handleEditKey(p.id, k.id)}>保存</button>
                                  <button className="btn btn-outline btn-sm" onClick={cancelEditKey}>取消</button>
                                </div>
                              ) : (
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                                  <span style={{ fontSize: 13, width: 80 }}>{k.alias || '默认'}</span>
                                  <code style={{ fontSize: 12, color: 'var(--text-muted)', flex: 1 }}>****{k.id}</code>
                                  <button className="btn btn-outline btn-sm" onClick={() => startEditKey(k)}>改 Key</button>
                                  <span className={`badge ${k.enabled ? 'badge-success' : 'badge-muted'}`} style={{ cursor: 'pointer' }} onClick={() => toggleKey(p.id, k.id, k.enabled)}>
                                    {k.enabled ? '启用' : '禁用'}
                                  </span>
                                  <button className="btn btn-danger btn-sm" onClick={() => handleDeleteKey(p.id, k.id)}>删除</button>
                                </div>
                              )}
                            </React.Fragment>
                          ))}
                          {/* Add key */}
                          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                            <input className="form-input" style={{ width: 100 }} value={newKeyAlias}
                              onChange={e => setNewKeyAlias(e.target.value)}
                              placeholder="别名（可选）" />
                            <input className="form-input" style={{ flex: 1 }} value={newKeyValue}
                              onChange={e => { setNewKeyValue(e.target.value); setNewKeyResult(null); }}
                              placeholder="粘贴新 API Key" />
                            <button className="btn btn-primary btn-sm" onClick={() => handleAddKey(p.id)}>添加</button>
                          </div>
                          {newKeyResult && (
                            <div style={{ marginTop: 8, background: 'var(--accent)', color: '#fff', padding: '8px 12px', borderRadius: 6, fontSize: 13, wordBreak: 'break-all' }}>
                              新 Key 已添加，请复制保存：{newKeyResult}
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                  {/* Model list row */}
                  {showModels === p.id && models[p.id] !== undefined && (
                    <tr key={`models-${p.id}`}>
                      <td colSpan={5} style={{ padding: '8px 0' }}>
                        <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 12 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
                            可用模型 ({models[p.id].length})
                          </div>
                          {models[p.id].length === 0 ? (
                            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>该厂商暂不支持获取模型列表</div>
                          ) : (
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                              {models[p.id].map(m => (
                                <span key={m} style={{
                                  background: 'var(--bg-tertiary)',
                                  color: 'var(--text-secondary)',
                                  padding: '2px 10px',
                                  borderRadius: 4,
                                  fontSize: 12,
                                  fontFamily: 'monospace'
                                }}>{m}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Add Modal ── */}
      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>添加工商</h2>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">选择厂商模板</label>
                <select className="form-select" value={form.template_name} onChange={e => onSelectTemplate(e.target.value)}>
                  <option value="">-- 选择厂商 --</option>
                  {templates.map(t => <option key={t.name} value={t.name}>{t.label}</option>)}
                </select>
              </div>
              {templateDetail && (
                <div style={{ background: 'var(--bg-tertiary)', borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 13 }}>
                  <div>Base URL：{templateDetail.base_url}</div>
                  <div style={{ marginTop: 4 }}>Chat：{templateDetail.api_path}</div>
                  <div style={{ marginTop: 4, display: 'flex', gap: 16 }}>
                    <span>模型列表：{templateDetail.models_path ? <span style={{color:'var(--accent)'}}>{templateDetail.models_path}</span> : <span style={{color:'var(--text-muted)'}}>不支持</span>}</span>
                    <span>余额查询：{templateDetail.balance_path ? <span style={{color:'var(--accent)'}}>{templateDetail.balance_path}</span> : <span style={{color:'var(--text-muted)'}}>不支持</span>}</span>
                  </div>
                </div>
              )}
              <div className="form-group">
                <label className="form-label">API Key</label>
                <input className="form-input" value={form.key_value}
                  onChange={e => setForm({ ...form, key_value: e.target.value })}
                  placeholder="粘贴厂商的 API Key" />
              </div>
              {testResult && (
                <div style={{ background: testResult.ok ? 'var(--success)' : 'var(--danger)', color: '#fff', padding: '12px 16px', borderRadius: 6, marginTop: 8, fontSize: 13 }}>
                  {testResult.ok ? '✓' : '✗'} {testResult.message}
                </div>
              )}
            </div>
            <div className="modal-actions">
              <button className="btn btn-outline btn-sm" onClick={handleTest} disabled={testing}>
                {testing ? '测试中...' : '测试连通'}
              </button>
              <div style={{ flex: 1 }} />
              <button className="btn btn-outline btn-sm" onClick={() => setShowAdd(false)}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handleAdd}>创建</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Edit Modal ── */}
      {showEdit && editProvider && (
        <div className="modal-overlay" onClick={() => setShowEdit(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>编辑 {editProvider.label}</h2>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">显示名称</label>
                <input className="form-input" value={editForm.label}
                  onChange={e => setEditForm({ ...editForm, label: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">API 基础地址</label>
                <input className="form-input" value={editForm.base_url}
                  onChange={e => setEditForm({ ...editForm, base_url: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">接口路径</label>
                <input className="form-input" value={editForm.api_path}
                  onChange={e => setEditForm({ ...editForm, api_path: e.target.value })} />
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn btn-outline btn-sm" onClick={() => setShowEdit(false)}>取消</button>
              <button className="btn btn-primary btn-sm" onClick={handleEdit}>保存</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
