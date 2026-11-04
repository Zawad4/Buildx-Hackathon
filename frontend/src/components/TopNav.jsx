import { Search, Bell, Menu } from 'lucide-react';
import { NAV_ITEMS } from '../navigation';

export default function TopNav({ activePage, onOpenMobile }) {
  const currentNav = NAV_ITEMS.find((item) => item.id === activePage);
  const pageTitle = currentNav ? currentNav.label : 'Overview';

  return (
    <header className="top-nav">
      <div className="top-nav-left">
        <button
          type="button"
          className="mobile-menu-btn"
          onClick={onOpenMobile}
          aria-label="Open navigation menu"
        >
          <Menu size={18} />
        </button>
        <div className="page-title-box">
          <span className="page-breadcrumb">ADAPTIVE VAULT X / Enclave</span>
          <h1 className="page-title">{pageTitle}</h1>
        </div>
      </div>

      <div className="top-nav-right">
        <div className="search-container">
          <Search className="search-icon" />
          <input
            type="search"
            className="search-input"
            placeholder="Search records, policies, logs..."
            aria-label="Search records, policies, logs"
          />
          <kbd className="search-shortcut">Ctrl+K</kbd>
        </div>

        <span className="enclave-badge">PCI-DSS Level 1</span>

        <div className="top-nav-divider" />

        <button
          type="button"
          className="icon-action-btn"
          aria-label="Notifications"
          title="Security Notifications"
        >
          <Bell size={16} />
          <span className="notification-badge">3</span>
        </button>

        <div className="user-profile">
          <div className="user-avatar" title="SecOps Administrator">
            SA
          </div>
          <div className="user-info">
            <span className="user-name">SecOps Admin</span>
            <span className="user-role">Financial Data Officer</span>
          </div>
        </div>
      </div>
    </header>
  );
}
