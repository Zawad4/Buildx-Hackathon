import { Shield, X } from 'lucide-react';
import { NAV_ITEMS } from '../navigation';

export default function Sidebar({ activePage, onSelectPage, mobileOpen, onCloseMobile }) {
  return (
    <>
      <div
        className={`mobile-backdrop ${mobileOpen ? 'visible' : ''}`}
        onClick={onCloseMobile}
        aria-hidden="true"
      />
      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-header">
          <div className="brand-link">
            <div className="brand-icon-box">
              <Shield size={18} strokeWidth={2.2} />
            </div>
            <div className="brand-meta">
              <span className="brand-title">ADAPTIVE VAULT X</span>
              <span className="brand-badge">Fintech Security Enclave</span>
            </div>
          </div>
          {mobileOpen && (
            <button
              type="button"
              className="mobile-menu-btn"
              onClick={onCloseMobile}
              aria-label="Close sidebar"
            >
              <X size={18} />
            </button>
          )}
        </div>

        <nav className="sidebar-nav">
          <div className="nav-label-group">Platform Navigation</div>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className={`nav-button ${isActive ? 'active' : ''}`}
                onClick={() => {
                  onSelectPage(item.id);
                  if (onCloseMobile) onCloseMobile();
                }}
              >
                <Icon className="nav-button-icon" strokeWidth={isActive ? 2.2 : 1.8} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="vault-status-card">
            <div className="vault-status-indicator">
              <span className="status-dot" />
              <span>Vault Core: Enforcing</span>
            </div>
            <p className="vault-status-desc">
              Vault Core: Enforcing (Sandbox Enclave)
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
