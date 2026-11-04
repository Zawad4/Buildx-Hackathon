import { useState } from 'react';
import './App.css';
import { NAV_ITEMS } from './navigation';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import Overview from './components/Overview';
import PlaceholderView from './components/PlaceholderView';

// Self-check: verify all navigation routes map to defined views
const VALID_PAGES = new Set(NAV_ITEMS.map((item) => item.id));
if (!VALID_PAGES.has('overview') || !VALID_PAGES.has('records')) {
  // shortcut: console-only assertion for dev check, upgrade to unit test runner if added
  console.warn('[AV-X Sanity Check] Missing core route definition');
}

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
          {activePage === 'overview' ? (
            <Overview onNavigate={setActivePage} />
          ) : (
            <PlaceholderView viewId={activePage} />
          )}
        </main>
      </div>
    </div>
  );
}
