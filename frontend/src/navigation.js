import {
  LayoutDashboard,
  Users,
  KeyRound,
  ShieldAlert,
  ScrollText,
  Settings,
} from 'lucide-react';

export const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'records', label: 'Customer Records', icon: Users },
  { id: 'access', label: 'Access Control', icon: KeyRound },
  { id: 'monitoring', label: 'Security Monitoring', icon: ShieldAlert },
  { id: 'audit', label: 'Audit Logs', icon: ScrollText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

