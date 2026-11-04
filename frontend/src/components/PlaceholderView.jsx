import {
  Users,
  KeyRound,
  ShieldAlert,
  ScrollText,
  Settings,
  Clock
} from 'lucide-react';

const VIEW_METADATA = {
  records: {
    title: 'Customer Records & PII Vault',
    desc: 'Encrypted token storage, dynamic field-level masking, and real-time anonymization views for high-value customer accounts.',
    icon: Users,
    stage: 'Stage 2 Component',
  },
  access: {
    title: 'Role-Based Access Control (RBAC)',
    desc: 'Granular egress permission policies, temporary elevation credentials, and cryptographic clearance keys.',
    icon: KeyRound,
    stage: 'Stage 2 Component',
  },
  monitoring: {
    title: 'Real-Time Security & DLP Monitoring',
    desc: 'Automated anomaly detection, high-entropy egress pattern inspection, and behavioral leakage alerts.',
    icon: ShieldAlert,
    stage: 'Stage 3 Component',
  },
  audit: {
    title: 'Immutable Compliance Audit Logs',
    desc: 'Cryptographically signed audit trail of every read, tokenization, decryption, and export transaction.',
    icon: ScrollText,
    stage: 'Stage 3 Component',
  },
  settings: {
    title: 'Enclave Security & Platform Settings',
    desc: 'Hardware security module (HSM) cluster configuration, key rotation schedules, and alert webhooks.',
    icon: Settings,
    stage: 'Settings Module',
  },
};

export default function PlaceholderView({ viewId }) {
  const meta = VIEW_METADATA[viewId] || {
    title: 'Section Under Construction',
    desc: 'This module is scheduled for implementation in upcoming stages.',
    icon: Clock,
    stage: 'Stage 1 Foundation',
  };

  const Icon = meta.icon;

  return (
    <div className="content-body">
      <div className="placeholder-container">
        <div className="placeholder-icon-box">
          <Icon size={26} strokeWidth={1.8} />
        </div>
        <h2 className="placeholder-title">{meta.title}</h2>
        <p className="placeholder-desc">{meta.desc}</p>
        <div className="placeholder-stage-badge">
          <Clock size={12} />
          <span>{meta.stage} · Foundation Shell Ready</span>
        </div>
      </div>
    </div>
  );
}

