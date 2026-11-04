import { useState, useEffect } from 'react';
import { Users, Search, KeyRound, ShieldCheck, X, RefreshCw, AlertCircle, FileText, CreditCard, DollarSign } from 'lucide-react';
import { api } from '../services/api';

export default function CustomerRecordsView() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCust, setSelectedCust] = useState(null);
  const [purpose, setPurpose] = useState('DISPUTE_RESOLUTION');
  const [ticketId, setTicketId] = useState('');
  const [role, setRole] = useState('SUPPORT');
  const [disclosedData, setDisclosedData] = useState(null);
  const [error, setError] = useState(null);

  const loadCustomers = (q = '') => {
    setLoading(true);
    api.getCustomers(q)
      .then(setCustomers)
      .catch((err) => console.error('Failed to load customers:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  const handleSearch = (e) => {
    const q = e.target.value;
    setSearch(q);
    loadCustomers(q);
  };

  const handleOpenModal = (cust) => {
    setSelectedCust(cust);
    setDisclosedData(null);
    setError(null);
  };

  const handleRequestAccess = async (e) => {
    e.preventDefault();
    if (!selectedCust) return;
    setError(null);
    setLoading(true);
    try {
      const username = role === 'SUPPORT' ? 'support_alice' : role === 'LOAN_OFFICER' ? 'loan_bob' : 'auditor_clara';
      const result = await api.requestCustomerAccess(selectedCust.id, purpose, ticketId, username);
      setDisclosedData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="content-body">
      <div className="panel-card">
        <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="panel-title-group">
            <div className="panel-title">
              <Users size={16} color="var(--brand-accent)" />
              <span>Customer Financial Records & PII Enclave</span>
            </div>
            <span className="panel-subtitle">
              Field-level AES-256-GCM ciphertexts decrypted on-demand via ABAC purpose validation
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="search"
              className="search-input"
              style={{ width: '260px' }}
              placeholder="Search by name or code (e.g. CUST-1002)..."
              value={search}
              onChange={handleSearch}
            />
            <button
              type="button"
              className="panel-action-btn"
              onClick={() => loadCustomers(search)}
            >
              <RefreshCw size={13} className={loading ? 'spin' : ''} /> Refresh
            </button>
          </div>
        </div>

        <div className="panel-body">
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Customer Code</th>
                  <th>Legal Identity</th>
                  <th>Contact Email</th>
                  <th>Masked Account No</th>
                  <th>Protected Phone</th>
                  <th>Risk Tier</th>
                  <th>KYC Status</th>
                  <th style={{ textAlign: 'right' }}>ABAC Action</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c.id}>
                    <td className="table-code font-bold" style={{ color: 'var(--brand-accent)' }}>
                      {c.customer_code}
                    </td>
                    <td className="font-medium">{c.full_name}</td>
                    <td className="table-code">{c.email}</td>
                    <td className="table-code font-bold">{c.account_number_masked}</td>
                    <td className="table-code">{c.phone_masked}</td>
                    <td>
                      <span className={`badge ${c.risk_tier === 'HIGH' ? 'badge-danger' : c.risk_tier === 'MEDIUM' ? 'badge-warning' : 'badge-neutral'}`}>
                        {c.risk_tier}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-accent">{c.kyc_status}</span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        type="button"
                        className="panel-action-btn"
                        onClick={() => handleOpenModal(c)}
                        style={{ padding: '4px 8px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        <KeyRound size={12} style={{ display: 'inline', marginRight: '4px' }} />
                        Request Access
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Purpose Modal / Disclosure Panel */}
      {selectedCust && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 100, backgroundColor: 'rgba(0,0,0,0.8)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px'
        }}>
          <div style={{
            background: 'var(--bg-panel, #111827)', border: '1px solid var(--border-subtle, #374151)',
            borderRadius: '12px', maxWidth: '600px', width: '100%', padding: '24px', position: 'relative',
            maxHeight: '90vh', overflowY: 'auto'
          }}>
            <button
              type="button"
              onClick={() => setSelectedCust(null)}
              style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer' }}
            >
              <X size={18} />
            </button>

            <h3 style={{ margin: '0 0 6px 0', fontSize: '16px', color: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={18} color="var(--brand-accent)" />
              Declare Purpose for {selectedCust.full_name} ({selectedCust.customer_code})
            </h3>
            <p style={{ margin: '0 0 16px 0', fontSize: '12px', color: '#9ca3af' }}>
              Select your role and declared business justification. The ABAC Policy Engine will determine permitted field disclosure.
            </p>

            {error && (
              <div style={{ padding: '10px 14px', background: 'rgba(220,38,38,0.2)', border: '1px solid #dc2626', borderRadius: '8px', color: '#fca5a5', fontSize: '12px', marginBottom: '16px' }}>
                <AlertCircle size={14} style={{ display: 'inline', marginRight: '6px' }} />
                {error}
              </div>
            )}

            {!disclosedData ? (
              <form onSubmit={handleRequestAccess} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#d1d5db', marginBottom: '4px' }}>
                    Requesting Role
                  </label>
                  <select
                    className="filter-select"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    style={{ width: '100%', padding: '8px' }}
                  >
                    <option value="SUPPORT">Alice Jenkins (Support - Allowed for Dispute & Inquiry)</option>
                    <option value="LOAN_OFFICER">Bob Martinez (Loan Officer - Allowed for Underwriting)</option>
                    <option value="COMPLIANCE_AUDITOR">Clara Oswald (Auditor - Full Clearance)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#d1d5db', marginBottom: '4px' }}>
                    Declared Business Purpose (ABAC Policy)
                  </label>
                  <select
                    className="filter-select"
                    value={purpose}
                    onChange={(e) => setPurpose(e.target.value)}
                    style={{ width: '100%', padding: '8px' }}
                  >
                    <option value="DISPUTE_RESOLUTION">Dispute Resolution (Unmasks Balance & Transactions; Redacts PAN)</option>
                    <option value="LOAN_UNDERWRITING">Loan Underwriting (Unmasks PAN & Balance; Redacts Transactions)</option>
                    <option value="GENERAL_INQUIRY">General Inquiry (Masked Overview)</option>
                    <option value="FRAUD_INVESTIGATION">Fraud Investigation (Full Disclosure)</option>
                    <option value="COMPLIANCE_AUDIT">Compliance Audit (Regulatory Audit Sample)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#d1d5db', marginBottom: '4px' }}>
                    Ticket / Case Reference
                  </label>
                  <input
                    type="text"
                    className="search-input"
                    placeholder="e.g. #TX-9042 or CASE-8821"
                    value={ticketId}
                    onChange={(e) => setTicketId(e.target.value)}
                    style={{ width: '100%' }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '12px' }}>
                  <button
                    type="button"
                    className="panel-action-btn"
                    onClick={() => setSelectedCust(null)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="panel-action-btn"
                    disabled={loading}
                    style={{ background: 'var(--brand-accent)', color: '#fff', border: 'none', fontWeight: 600 }}
                  >
                    {loading ? 'Evaluating Policy...' : 'Evaluate & Decrypt Fields'}
                  </button>
                </div>
              </form>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ padding: '8px 12px', background: 'rgba(22,163,74,0.15)', border: '1px solid #16a34a', borderRadius: '8px', fontSize: '12px', color: '#86efac' }}>
                  Policy Verified: Access Granted for <strong>{disclosedData.access_meta.purpose}</strong> (+{disclosedData.access_meta.exposure_points_charged} pts charged)
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px', border: '1px solid #374151' }}>
                    <span style={{ fontSize: '11px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CreditCard size={12} /> Account Number
                    </span>
                    <div style={{ fontSize: '13px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f3f4f6', marginTop: '4px' }}>
                      {disclosedData.account_number}
                    </div>
                  </div>

                  <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px', border: '1px solid #374151' }}>
                    <span style={{ fontSize: '11px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <FileText size={12} /> PAN Tax ID
                    </span>
                    <div style={{ fontSize: '13px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f3f4f6', marginTop: '4px' }}>
                      {disclosedData.pan}
                    </div>
                  </div>

                  <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px', border: '1px solid #374151' }}>
                    <span style={{ fontSize: '11px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <DollarSign size={12} /> Balance
                    </span>
                    <div style={{ fontSize: '13px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f3f4f6', marginTop: '4px' }}>
                      {disclosedData.balance}
                    </div>
                  </div>

                  <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px', border: '1px solid #374151' }}>
                    <span style={{ fontSize: '11px', color: '#9ca3af' }}>Credit Score</span>
                    <div style={{ fontSize: '13px', fontWeight: 'bold', fontFamily: 'monospace', color: '#60a5fa', marginTop: '4px' }}>
                      {disclosedData.credit_score !== null ? `${disclosedData.credit_score} (CIBIL)` : '[REDACTED]'}
                    </div>
                  </div>
                </div>

                {disclosedData.transactions.length > 0 && (
                  <div style={{ marginTop: '8px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: '#d1d5db' }}>
                      AES-256-GCM Decrypted Transactions ({disclosedData.transactions.length}):
                    </span>
                    <div style={{ maxHeight: '120px', overflowY: 'auto', marginTop: '6px' }}>
                      {disclosedData.transactions.map((tx) => (
                        <div key={tx.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px', borderBottom: '1px solid #374151', fontSize: '11px' }}>
                          <span>{tx.merchant} ({tx.category})</span>
                          <span style={{ fontWeight: 'bold', fontFamily: 'monospace' }}>{tx.amount}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  type="button"
                  className="panel-action-btn"
                  onClick={() => setDisclosedData(null)}
                  style={{ marginTop: '12px' }}
                >
                  Test Another Purpose / Record
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
