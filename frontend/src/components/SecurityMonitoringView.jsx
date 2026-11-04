import { useState, useEffect } from 'react';
import { ShieldAlert, Cpu, AlertTriangle, Zap, CheckCircle2, ShieldX, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function SecurityMonitoringView() {
  const [incidents, setIncidents] = useState([]);
  const [pqcResult, setPqcResult] = useState(null);
  const [exfilResult, setExfilResult] = useState(null);
  const [loadingPqc, setLoadingPqc] = useState(false);
  const [loadingExfil, setLoadingExfil] = useState(false);

  const loadIncidents = () => {
    api.getSecurityIncidents()
      .then(setIncidents)
      .catch((err) => console.error('Failed to load incidents:', err));
  };

  useEffect(() => {
    loadIncidents();
  }, []);

  const handleRunPqc = async () => {
    setLoadingPqc(true);
    setPqcResult(null);
    try {
      const res = await api.runPqcHandshake();
      setPqcResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPqc(false);
    }
  };

  const handleSimulateExfiltration = async () => {
    setLoadingExfil(true);
    setExfilResult(null);
    try {
      await api.triggerBulkExportAttack();
      setExfilResult({ success: true, text: 'Export completed (Unchecked)' });
    } catch (err) {
      setExfilResult({ success: false, text: err.message });
      loadIncidents();
    } finally {
      setLoadingExfil(false);
    }
  };

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Top Interactive Demos: Exfiltration Blocker & PQC */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        
        {/* Active Exfiltration Blocker Card */}
        <div className="panel-card">
          <div className="panel-header">
            <div className="panel-title-group">
              <div className="panel-title">
                <ShieldX size={16} color="var(--status-danger-text)" />
                <span>Active Exfiltration Blocker (Attack Simulator)</span>
              </div>
              <span className="panel-subtitle">
                Tests automated session locking when an insider attempts bulk PII exports
              </span>
            </div>
          </div>
          <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <p style={{ fontSize: '12px', color: '#9ca3af', margin: 0 }}>
              Click below to simulate an employee script attempting to extract 15 unmasked customer records simultaneously.
            </p>

            <button
              type="button"
              className="panel-action-btn"
              onClick={handleSimulateExfiltration}
              disabled={loadingExfil}
              style={{ background: 'rgba(220,38,38,0.2)', border: '1px solid #dc2626', color: '#fca5a5', fontWeight: 600, padding: '8px 14px' }}
            >
              <AlertTriangle size={14} style={{ display: 'inline', marginRight: '6px' }} />
              {loadingExfil ? 'Executing Attack Simulation...' : 'Simulate Bulk Export Exfiltration (15 Records)'}
            </button>

            {exfilResult && (
              <div style={{
                padding: '10px 14px', borderRadius: '8px', fontSize: '12px',
                background: exfilResult.success ? 'rgba(22,163,74,0.2)' : 'rgba(220,38,38,0.2)',
                border: exfilResult.success ? '1px solid #16a34a' : '1px solid #dc2626',
                color: exfilResult.success ? '#86efac' : '#fca5a5'
              }}>
                <strong>Active Defense Result:</strong> {exfilResult.text}
              </div>
            )}
          </div>
        </div>

        {/* Post-Quantum KEM Card */}
        <div className="panel-card">
          <div className="panel-header">
            <div className="panel-title-group">
              <div className="panel-title">
                <Cpu size={16} color="var(--brand-accent)" />
                <span>Post-Quantum Key Establishment (ML-KEM-768)</span>
              </div>
              <span className="panel-subtitle">
                NIST FIPS 203 Module-Lattice Key Encapsulation (Defeats Harvest Now, Decrypt Later)
              </span>
            </div>
          </div>
          <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <p style={{ fontSize: '12px', color: '#9ca3af', margin: 0 }}>
              Execute a live quantum-resistant lattice handshake establishing a 256-bit symmetric session key.
            </p>

            <button
              type="button"
              className="panel-action-btn"
              onClick={handleRunPqc}
              disabled={loadingPqc}
              style={{ background: 'rgba(59,130,246,0.2)', border: '1px solid #3b82f6', color: '#93c5fd', fontWeight: 600, padding: '8px 14px' }}
            >
              <Zap size={14} style={{ display: 'inline', marginRight: '6px' }} />
              {loadingPqc ? 'Computing Lattice Polynomials...' : 'Execute ML-KEM-768 Handshake'}
            </button>

            {pqcResult && (
              <div style={{ padding: '10px 14px', borderRadius: '8px', fontSize: '11px', background: 'rgba(59,130,246,0.15)', border: '1px solid #3b82f6', color: '#dbeafe', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold' }}>
                  <span>Handshake Verified: {pqcResult.handshake_verified ? 'TRUE (100% Match)' : 'FALSE'}</span>
                  <span style={{ color: '#86efac' }}>Latency: {pqcResult.metrics.total_handshake_ms} ms</span>
                </div>
                <div>Public Key: {pqcResult.metrics.public_key_bytes} Bytes • Ciphertext: {pqcResult.metrics.ciphertext_bytes} Bytes</div>
                <div style={{ fontFamily: 'monospace', fontSize: '10px', color: '#6ee7b7', wordBreak: 'break-all' }}>
                  AES Key: {pqcResult.hex_previews.established_shared_key}
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Security Incidents Table from SQLite */}
      <div className="panel-card">
        <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="panel-title-group">
            <div className="panel-title">
              <ShieldAlert size={16} color="var(--status-danger-text)" />
              <span>Real-Time Security Incident Feed (SQLite Live)</span>
            </div>
            <span className="panel-subtitle">
              Live alerts recorded when employees exceed quotas, attempt exfiltration, or trigger velocity thresholds
            </span>
          </div>

          <button type="button" className="panel-action-btn" onClick={loadIncidents}>
            <RefreshCw size={13} /> Refresh Incidents
          </button>
        </div>

        <div className="panel-body">
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Incident ID</th>
                  <th>Incident Type</th>
                  <th>Actor / IP</th>
                  <th>Severity</th>
                  <th>Timestamp</th>
                  <th>Enforcement Action</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {incidents.map((inc) => (
                  <tr key={inc.id}>
                    <td className="table-code font-bold">{inc.id}</td>
                    <td className="font-semibold">{inc.incident_type}</td>
                    <td className="table-code">{inc.username} ({inc.ip_address})</td>
                    <td>
                      <span className={`badge ${inc.severity === 'CRITICAL' ? 'badge-danger' : inc.severity === 'HIGH' ? 'badge-warning' : 'badge-neutral'}`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="table-timestamp">{inc.timestamp}</td>
                    <td>
                      <span className={`status-pill ${inc.blocked ? 'status-denied' : 'status-flagged'}`}>
                        {inc.blocked ? 'BLOCKED' : 'FLAGGED'}
                      </span>
                    </td>
                    <td style={{ fontSize: '11px', color: '#d1d5db' }}>{inc.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  );
}
