import { useState } from 'react';
import './App.css';
import { NAV_ITEMS } from './navigation';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import Overview from './components/Overview';
import CustomerRecordsView from './components/CustomerRecordsView';
import SecurityMonitoringView from './components/SecurityMonitoringView';
import AuditTrailView from './components/AuditTrailView';
import PlaceholderView from './components/PlaceholderView';

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        onSelectPage={setActivePage}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <div className="app-main">
        <TopNav
          activePage={activePage}
          onOpenMobile={() => setMobileOpen(true)}
        />

        <main>
          {activePage === 'overview' && <Overview onNavigate={setActivePage} />}
          {activePage === 'records' && <CustomerRecordsView />}
          {activePage === 'monitoring' && <SecurityMonitoringView />}
          {activePage === 'audit' && <AuditTrailView />}
          {activePage !== 'overview' &&
            activePage !== 'records' &&
            activePage !== 'monitoring' &&
            activePage !== 'audit' && (
              <PlaceholderView viewId={activePage} />
            )}
        </main>
      </div>
    </div>
  );
}
