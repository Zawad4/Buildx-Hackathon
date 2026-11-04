const API_BASE = '/api/v1';

export const api = {
  async getDashboardSummary() {
    const res = await fetch(`${API_BASE}/audit/dashboard-summary`);
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },

  async getCustomers(query = '') {
    const url = query ? `${API_BASE}/customers?q=${encodeURIComponent(query)}` : `${API_BASE}/customers`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch customer records');
    return res.json();
  },

  async getPurposes(role = 'SUPPORT') {
    const res = await fetch(`${API_BASE}/customers/purposes?role=${encodeURIComponent(role)}`);
    if (!res.ok) throw new Error('Failed to fetch purposes');
    return res.json();
  },

  async requestCustomerAccess(customerId, purpose, ticketId = '', username = 'support_alice') {
    const res = await fetch(`${API_BASE}/customers/${customerId}/access`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ purpose, ticket_id: ticketId, username })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Access denied by policy');
    }
    return res.json();
  },

  async triggerBulkExportAttack() {
    const res = await fetch(`${API_BASE}/customers/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_ids: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], purpose: 'GENERAL_INQUIRY' })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Export blocked');
    }
    return res.json();
  },

  async getAuditLogs(params = {}) {
    const qs = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/audit/logs?${qs}`);
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  async getSecurityIncidents() {
    const res = await fetch(`${API_BASE}/audit/incidents`);
    if (!res.ok) throw new Error('Failed to fetch security incidents');
    return res.json();
  },

  async runPqcHandshake() {
    const res = await fetch(`${API_BASE}/crypto/pqc-handshake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to execute PQC handshake');
    return res.json();
  }
};
