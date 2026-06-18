import React from 'react';
import { invoiceStatusLabel, paymentStatusLabel } from '../utils/formatting';

const INVOICE_VARIANTS = {
  UNPAID: 'bg-red-50 text-red-700 ring-red-200',
  PARTIALLY_PAID: 'bg-amber-50 text-amber-700 ring-amber-200',
  PAID: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  OVERDUE: 'bg-orange-50 text-orange-700 ring-orange-200',
  CANCELED: 'bg-gray-100 text-gray-500 ring-gray-200',
};

const PAYMENT_VARIANTS = {
  SUCCESS: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  CANCELED: 'bg-gray-100 text-gray-500 ring-gray-200',
  REFUNDED: 'bg-purple-50 text-purple-700 ring-purple-200',
};

const CLASS_VARIANTS = {
  ACTIVE: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  PAUSED: 'bg-amber-50 text-amber-700 ring-amber-200',
  COMPLETED: 'bg-blue-50 text-blue-700 ring-blue-200',
  CANCELED: 'bg-gray-100 text-gray-500 ring-gray-200',
};

const VARIANTS = {
  invoice: INVOICE_VARIANTS,
  payment: PAYMENT_VARIANTS,
  class: CLASS_VARIANTS,
};

const LABELS = {
  invoice: invoiceStatusLabel,
  payment: paymentStatusLabel,
};

export default function StatusBadge({ status, variant = 'invoice' }) {
  if (!status) return null;
  const palette = VARIANTS[variant] || INVOICE_VARIANTS;
  const classes = palette[status] || 'bg-gray-100 text-gray-700 ring-gray-200';
  const labelFn = LABELS[variant];
  const label = labelFn ? labelFn(status) : status;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${classes}`}
    >
      {label}
    </span>
  );
}
