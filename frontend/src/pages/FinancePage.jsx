import React, { useEffect, useMemo, useState } from 'react';
import {
  createInvoice,
  createPayment,
  deleteInvoice,
  deletePayment,
  getClassInvoicePeriod,
  getClassTuitionSummary,
  listClasses,
  listInvoices,
  listPayments,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  PAYMENT_METHOD_KEYS,
  PAYMENT_METHOD_LABELS,
  formatCurrency,
  formatDate,
  invoiceStatusLabel,
  paymentStatusLabel,
} from '../utils/formatting';
import ConfirmDialog from '../components/ConfirmDialog';
import StatusBadge from '../components/StatusBadge';

const emptyInvoice = {
  class_id: '',
  period_start: '',
  period_end: '',
  completed_sessions: '',
  tuition_fee_per_session: '',
  amount_due: '',
  status: 'UNPAID',
  autoAmount: true,
};

const emptyPayment = {
  invoice_id: '',
  amount_paid: '',
  payment_method: 'BANK_TRANSFER',
  note: '',
};

const SORT_DIRECTIONS = { asc: 'asc', desc: 'desc' };

function sortData(rows, sortKey, direction) {
  if (!sortKey) return rows;
  const dir = direction === SORT_DIRECTIONS.desc ? -1 : 1;
  return [...rows].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir;
    return String(av).localeCompare(String(bv), 'vi-VN') * dir;
  });
}

function filterRows(rows, query, predicate) {
  const q = query.trim().toLowerCase();
  if (!q) return rows;
  return rows.filter((row) => predicate(row, q));
}

export default function FinancePage() {
  const { user } = useAuth();
  const isStaff = user?.role === 'staff';
  const isStudent = user?.role === 'student';
  const canView = isStaff || isStudent;

  const [classes, setClasses] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('invoices');
  const [showInvoiceForm, setShowInvoiceForm] = useState(false);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [invoiceForm, setInvoiceForm] = useState(emptyInvoice);
  const [paymentForm, setPaymentForm] = useState(emptyPayment);
  const [saving, setSaving] = useState(false);
  const [tuitionSummary, setTuitionSummary] = useState(null);

  const [invoiceSearch, setInvoiceSearch] = useState('');
  const [paymentSearch, setPaymentSearch] = useState('');
  const [invoiceSort, setInvoiceSort] = useState({ key: 'period_start', dir: 'desc' });
  const [paymentSort, setPaymentSort] = useState({ key: 'id', dir: 'desc' });

  const [invoiceFormError, setInvoiceFormError] = useState('');
  const [paymentFormError, setPaymentFormError] = useState('');
  const [invoiceFieldError, setInvoiceFieldError] = useState({});
  const [paymentFieldError, setPaymentFieldError] = useState({});

  const [pendingCancel, setPendingCancel] = useState(null); // { type: 'invoice'|'payment', id, loading }
  const [confirmResetForm, setConfirmResetForm] = useState(null); // { kind: 'invoice'|'payment' }

  useEffect(() => {
    if (!canView || !user) return undefined;
    let active = true;
    const filters = isStudent ? { student_id: user.id } : {};
    Promise.all([listInvoices(filters), listPayments(filters), listClasses(filters)])
      .then(([invoiceData, paymentData, classData]) => {
        if (!active) return;
        setInvoices(Array.isArray(invoiceData) ? invoiceData : []);
        setPayments(Array.isArray(paymentData) ? paymentData : []);
        setClasses(Array.isArray(classData) ? classData : []);
      })
      .catch((err) => active && setError(err?.message || 'Không tải được dữ liệu học phí'))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [canView, isStudent, user]);

  const classMap = useMemo(
    () => Object.fromEntries(classes.map((item) => [item.id, item])),
    [classes],
  );

  const selectedInvoice = useMemo(
    () => invoices.find((i) => String(i.id) === String(paymentForm.invoice_id)) || null,
    [invoices, paymentForm.invoice_id],
  );
  const selectedRemaining = selectedInvoice
    ? Math.max(0, Number(selectedInvoice.amount_due || 0) - Number(selectedInvoice.amount_paid || 0))
    : 0;
  const paymentAmount = Number(paymentForm.amount_paid || 0);
  const paymentOverpay = paymentAmount > selectedRemaining;
  const paymentInvalid =
    !!paymentForm.invoice_id && (!Number.isFinite(paymentAmount) || paymentAmount <= 0 || paymentOverpay);

  const invoiceDuplicate = useMemo(() => {
    if (!invoiceForm.class_id || !invoiceForm.period_start || !invoiceForm.period_end) return null;
    return (
      invoices.find(
        (i) =>
          i.class_id === Number(invoiceForm.class_id) &&
          i.period_start === invoiceForm.period_start &&
          i.period_end === invoiceForm.period_end &&
          i.status !== 'CANCELED',
      ) || null
    );
  }, [invoices, invoiceForm.class_id, invoiceForm.period_start, invoiceForm.period_end]);

  const handleClassSelect = async (classId) => {
    setInvoiceFieldError({});
    setInvoiceFormError('');
    setInvoiceForm((prev) => ({ ...prev, class_id: classId, autoAmount: true }));
    if (!classId) {
      setTuitionSummary(null);
      return;
    }
    try {
      const [summary, period] = await Promise.all([
        getClassTuitionSummary(Number(classId)),
        getClassInvoicePeriod(Number(classId)),
      ]);
      setTuitionSummary(summary);
      const sessions = Number(summary.completed_sessions || 0);
      const fee = Number(summary.tuition_fee_per_session || 0);
      setInvoiceForm((prev) => ({
        ...prev,
        class_id: classId,
        period_start: period.period_start,
        period_end: period.period_end,
        completed_sessions: String(sessions),
        tuition_fee_per_session: String(fee),
        amount_due: String(sessions * fee),
        autoAmount: true,
      }));
    } catch {
      setTuitionSummary(null);
    }
  };

  const updateInvoiceNumber = (field, value) => {
    setInvoiceFieldError((prev) => ({ ...prev, [field]: '' }));
    setInvoiceForm((prev) => {
      const next = { ...prev, [field]: value };
      if (field === 'completed_sessions' || field === 'tuition_fee_per_session') {
        const sessions = Number(field === 'completed_sessions' ? value : prev.completed_sessions || 0);
        const fee = Number(field === 'tuition_fee_per_session' ? value : prev.tuition_fee_per_session || 0);
        if (prev.autoAmount) {
          next.amount_due = String(Math.max(0, sessions) * Math.max(0, fee));
        }
      } else if (field === 'amount_due') {
        next.autoAmount = false;
      }
      return next;
    });
  };

  const validateInvoice = () => {
    const errs = {};
    if (!invoiceForm.class_id) errs.class_id = 'Vui lòng chọn lớp.';
    if (!invoiceForm.period_start) errs.period_start = 'Vui lòng chọn ngày bắt đầu.';
    if (!invoiceForm.period_end) errs.period_end = 'Vui lòng chọn ngày kết thúc.';
    if (
      invoiceForm.period_start &&
      invoiceForm.period_end &&
      invoiceForm.period_end < invoiceForm.period_start
    ) {
      errs.period_end = 'Ngày kết thúc phải sau ngày bắt đầu.';
    }
    const sessions = Number(invoiceForm.completed_sessions);
    if (!Number.isFinite(sessions) || sessions < 0) errs.completed_sessions = 'Số buổi phải ≥ 0.';
    const fee = Number(invoiceForm.tuition_fee_per_session);
    if (!Number.isFinite(fee) || fee <= 0) errs.tuition_fee_per_session = 'Phí/buổi phải > 0.';
    const amount = Number(invoiceForm.amount_due);
    if (!Number.isFinite(amount) || amount <= 0) errs.amount_due = 'Tổng tiền phải > 0.';
    if (invoiceDuplicate) errs.period_end = `Kỳ này đã có invoice #${invoiceDuplicate.id}.`;
    setInvoiceFieldError(errs);
    return Object.keys(errs).length === 0;
  };

  const handleInvoiceCreate = async (e) => {
    e.preventDefault();
    if (!validateInvoice()) return;
    setSaving(true);
    setError('');
    setInvoiceFormError('');
    try {
      const payload = {
        class_id: Number(invoiceForm.class_id),
        period_start: invoiceForm.period_start,
        period_end: invoiceForm.period_end,
        completed_sessions: Number(invoiceForm.completed_sessions || 0),
        tuition_fee_per_session: Number(invoiceForm.tuition_fee_per_session || 0),
        amount_due: Number(invoiceForm.amount_due || 0),
        amount_paid: 0,
        status: 'UNPAID',
      };
      const created = await createInvoice(payload);
      setInvoices((prev) => [created, ...prev]);
      setInvoiceForm(emptyInvoice);
      setTuitionSummary(null);
      setInvoiceFieldError({});
      setShowInvoiceForm(false);
    } catch (err) {
      setInvoiceFormError(err?.message || 'Không tạo được hóa đơn');
    } finally {
      setSaving(false);
    }
  };

  const handlePaymentCreate = async (e) => {
    e.preventDefault();
    if (paymentInvalid) return;
    setSaving(true);
    setError('');
    setPaymentFormError('');
    try {
      const created = await createPayment({
        invoice_id: Number(paymentForm.invoice_id),
        amount_paid: paymentAmount,
        payment_method: paymentForm.payment_method,
        note: paymentForm.note || null,
        staff_id: isStaff ? user.id : null,
      });
      setPayments((prev) => [created, ...prev]);
      const filters = isStudent ? { student_id: user.id } : {};
      const freshInvoices = await listInvoices(filters);
      setInvoices(Array.isArray(freshInvoices) ? freshInvoices : []);
      if (tuitionSummary && selectedInvoice && Number(selectedInvoice.class_id) === Number(invoiceForm.class_id || 0)) {
        try {
          const [summary, period] = await Promise.all([
            getClassTuitionSummary(Number(invoiceForm.class_id)),
            getClassInvoicePeriod(Number(invoiceForm.class_id)),
          ]);
          setTuitionSummary(summary);
          setInvoiceForm((prev) => ({
            ...prev,
            period_start: period.period_start,
            period_end: period.period_end,
            completed_sessions: String(summary.completed_sessions),
            tuition_fee_per_session: String(summary.tuition_fee_per_session),
            amount_due: String(summary.remaining_amount > 0 ? summary.total_fee : 0),
            autoAmount: true,
          }));
        } catch {
          // ignore refresh error
        }
      }
      setPaymentForm(emptyPayment);
      setPaymentFieldError({});
      setShowPaymentForm(false);
    } catch (err) {
      setPaymentFormError(err?.message || 'Không ghi nhận được thanh toán');
    } finally {
      setSaving(false);
    }
  };

  const performCancel = async () => {
    if (!pendingCancel) return;
    const { type, id } = pendingCancel;
    setPendingCancel((prev) => (prev ? { ...prev, loading: true } : prev));
    try {
      if (type === 'invoice') {
        await deleteInvoice(id);
        setInvoices((prev) =>
          prev.map((item) => (item.id === id ? { ...item, status: 'CANCELED' } : item)),
        );
      } else {
        await deletePayment(id);
        const filters = isStudent ? { student_id: user.id } : {};
        const [freshPayments, freshInvoices] = await Promise.all([
          listPayments(filters),
          listInvoices(filters),
        ]);
        setPayments(Array.isArray(freshPayments) ? freshPayments : []);
        setInvoices(Array.isArray(freshInvoices) ? freshInvoices : []);
      }
      setPendingCancel(null);
    } catch (err) {
      setError(err?.message || (type === 'invoice' ? 'Không hủy được hóa đơn' : 'Không hủy được thanh toán'));
      setPendingCancel(null);
    }
  };

  const toggleInvoiceForm = () => {
    setShowInvoiceForm((prev) => {
      const next = !prev;
      if (next) {
        setShowPaymentForm(false);
        setPaymentFormError('');
      } else {
        setInvoiceForm(emptyInvoice);
        setInvoiceFieldError({});
        setInvoiceFormError('');
        setTuitionSummary(null);
      }
      return next;
    });
  };

  const togglePaymentForm = () => {
    setShowPaymentForm((prev) => {
      const next = !prev;
      if (next) {
        setShowInvoiceForm(false);
        setInvoiceFormError('');
      } else {
        setPaymentForm(emptyPayment);
        setPaymentFieldError({});
        setPaymentFormError('');
      }
      return next;
    });
  };

  const toggleSort = (key, current) => {
    if (current.key !== key) return { key, dir: 'desc' };
    if (current.dir === 'desc') return { key, dir: 'asc' };
    return { key: '', dir: 'desc' };
  };

  const filteredInvoices = useMemo(
    () =>
      filterRows(invoices, invoiceSearch, (row, q) => {
        const cls = classMap[row.class_id]?.code || `Class #${row.class_id}`;
        const status = invoiceStatusLabel(row.status).toLowerCase();
        return (
          String(row.id).includes(q) ||
          cls.toLowerCase().includes(q) ||
          status.includes(q) ||
          formatDate(row.period_start).includes(q) ||
          formatDate(row.period_end).includes(q)
        );
      }),
    [invoices, invoiceSearch, classMap],
  );

  const filteredPayments = useMemo(
    () =>
      filterRows(payments, paymentSearch, (row, q) => {
        const cls = classMap[row.class_id]?.code || row.className || '';
        const status = paymentStatusLabel(row.status).toLowerCase();
        return (
          String(row.id).includes(q) ||
          cls.toLowerCase().includes(q) ||
          status.includes(q) ||
          (row.note || '').toLowerCase().includes(q)
        );
      }),
    [payments, paymentSearch, classMap],
  );

  const sortedInvoices = useMemo(
    () => sortData(filteredInvoices, invoiceSort.key, invoiceSort.dir),
    [filteredInvoices, invoiceSort],
  );
  const sortedPayments = useMemo(
    () => sortData(filteredPayments, paymentSort.key, paymentSort.dir),
    [filteredPayments, paymentSort],
  );

  if (!user) {
    return <div className="rounded-lg bg-white p-6 shadow">Vui lòng đăng nhập để xem học phí.</div>;
  }

  if (!canView) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-600">
        Chỉ staff hoặc học viên sở hữu mới xem được hóa đơn và thanh toán.
      </div>
    );
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow">Đang tải dữ liệu tài chính...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isStaff ? 'Quản lý học phí và thanh toán' : 'Học phí của tôi'}
          </h1>
          <p className="text-sm text-gray-500">Theo dõi invoice snapshot và payment thực tế.</p>
        </div>
        {isStaff && (
          <div className="flex gap-2">
            <button
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              onClick={toggleInvoiceForm}
            >
              {showInvoiceForm ? 'Đóng form hóa đơn' : 'Tạo hóa đơn'}
            </button>
            <button
              className="rounded-lg bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700"
              onClick={togglePaymentForm}
            >
              {showPaymentForm ? 'Đóng form thanh toán' : 'Ghi nhận thanh toán'}
            </button>
          </div>
        )}
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="flex gap-2">
        <button
          className={`flex items-center gap-2 rounded-lg px-4 py-2 ${
            activeTab === 'invoices' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'
          }`}
          onClick={() => setActiveTab('invoices')}
        >
          <span>Hóa đơn</span>
          <span
            className={`inline-flex min-w-[28px] justify-center rounded-full px-2 py-0.5 text-xs ${
              activeTab === 'invoices' ? 'bg-white/20' : 'bg-gray-100'
            }`}
          >
            {invoices.length}
          </span>
        </button>
        <button
          className={`flex items-center gap-2 rounded-lg px-4 py-2 ${
            activeTab === 'payments' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'
          }`}
          onClick={() => setActiveTab('payments')}
        >
          <span>Thanh toán</span>
          <span
            className={`inline-flex min-w-[28px] justify-center rounded-full px-2 py-0.5 text-xs ${
              activeTab === 'payments' ? 'bg-white/20' : 'bg-gray-100'
            }`}
          >
            {payments.length}
          </span>
        </button>
      </div>

      {showInvoiceForm && isStaff && (
        <form
          onSubmit={handleInvoiceCreate}
          className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2"
        >
          {invoiceFormError && (
            <div className="md:col-span-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {invoiceFormError}
            </div>
          )}
          <div className="md:col-span-2">
            <label className="mb-1 block text-xs font-medium text-gray-600">Lớp</label>
            <select
              className={`w-full rounded-lg border px-3 py-2 ${
                invoiceFieldError.class_id ? 'border-red-500 bg-red-50' : 'border-gray-200'
              }`}
              value={invoiceForm.class_id}
              onChange={(e) => handleClassSelect(e.target.value)}
              required
            >
              <option value="">Chọn lớp</option>
              {classes.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.code} - {item.subject} - {item.student}
                </option>
              ))}
            </select>
            {invoiceFieldError.class_id && (
              <p className="mt-1 text-xs text-red-600">{invoiceFieldError.class_id}</p>
            )}
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Kỳ bắt đầu</label>
            <input
              className={`w-full rounded-lg border px-3 py-2 ${
                invoiceFieldError.period_start ? 'border-red-500 bg-red-50' : 'border-gray-200'
              }`}
              type="date"
              value={invoiceForm.period_start}
              onChange={(e) => {
                setInvoiceFieldError((prev) => ({ ...prev, period_start: '' }));
                setInvoiceForm((prev) => ({ ...prev, period_start: e.target.value }));
              }}
              required
            />
            {invoiceFieldError.period_start && (
              <p className="mt-1 text-xs text-red-600">{invoiceFieldError.period_start}</p>
            )}
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Kỳ kết thúc</label>
            <input
              className={`w-full rounded-lg border px-3 py-2 ${
                invoiceFieldError.period_end ? 'border-red-500 bg-red-50' : 'border-gray-200'
              }`}
              type="date"
              value={invoiceForm.period_end}
              onChange={(e) => {
                setInvoiceFieldError((prev) => ({ ...prev, period_end: '' }));
                setInvoiceForm((prev) => ({ ...prev, period_end: e.target.value }));
              }}
              required
            />
            {invoiceFieldError.period_end && (
              <p className="mt-1 text-xs text-red-600">{invoiceFieldError.period_end}</p>
            )}
          </div>

          {tuitionSummary && (
            <div className="md:col-span-2 rounded-lg bg-blue-50 p-4 text-sm">
              <div className="mb-2 flex items-center justify-between">
                <div className="font-semibold text-blue-900">Tóm tắt học phí (realtime)</div>
                <div className="text-xs text-blue-700">
                  Kỳ gợi ý: {invoiceForm.period_start} → {invoiceForm.period_end}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-blue-800 md:grid-cols-4">
                <div>
                  Hoàn thành: <span className="font-semibold">{tuitionSummary.completed_sessions}</span> buổi
                </div>
                <div>
                  Phí/buổi:{' '}
                  <span className="font-semibold">
                    {formatCurrency(tuitionSummary.tuition_fee_per_session)}
                  </span>
                </div>
                <div>
                  Tổng phí: <span className="font-semibold">{formatCurrency(tuitionSummary.total_fee)}</span>
                </div>
                <div>
                  Còn nợ:{' '}
                  <span className="font-semibold text-red-600">
                    {formatCurrency(tuitionSummary.remaining_amount)}
                  </span>
                </div>
              </div>
              <div className="mt-2 text-xs italic text-blue-600">
                Số buổi, phí/buổi và tổng tiền đã được tự động điền. Bạn có thể chỉnh nếu cần.
              </div>
            </div>
          )}

          {invoiceDuplicate && (
            <div className="md:col-span-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
              ⚠ Đã có invoice #{invoiceDuplicate.id} cho lớp này trong kỳ{' '}
              {formatDate(invoiceDuplicate.period_start)} → {formatDate(invoiceDuplicate.period_end)}. Hãy đổi
              kỳ khác hoặc hủy invoice cũ trước khi tạo mới.
            </div>
          )}

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Số buổi hoàn thành</label>
            <input
              className={`w-full rounded-lg border px-3 py-2 ${
                invoiceFieldError.completed_sessions
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 bg-blue-50'
              }`}
              type="number"
              min="0"
              value={invoiceForm.completed_sessions}
              onChange={(e) => updateInvoiceNumber('completed_sessions', e.target.value)}
              required
            />
            {invoiceFieldError.completed_sessions && (
              <p className="mt-1 text-xs text-red-600">{invoiceFieldError.completed_sessions}</p>
            )}
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Học phí / buổi</label>
            <input
              className={`w-full rounded-lg border px-3 py-2 ${
                invoiceFieldError.tuition_fee_per_session
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 bg-blue-50'
              }`}
              type="number"
              min="0"
              value={invoiceForm.tuition_fee_per_session}
              onChange={(e) => updateInvoiceNumber('tuition_fee_per_session', e.target.value)}
              required
            />
            {invoiceFieldError.tuition_fee_per_session && (
              <p className="mt-1 text-xs text-red-600">{invoiceFieldError.tuition_fee_per_session}</p>
            )}
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Tổng tiền phải thu {invoiceForm.autoAmount ? '(tự tính = buổi × phí/buổi)' : '(đã chỉnh thủ công)'}
            </label>
            <input
              className={`w-full rounded-lg border px-3 py-2 ${
                invoiceFieldError.amount_due ? 'border-red-500 bg-red-50' : 'border-gray-200 bg-blue-50'
              }`}
              type="number"
              min="0"
              value={invoiceForm.amount_due}
              onChange={(e) => updateInvoiceNumber('amount_due', e.target.value)}
              required
            />
            {invoiceFieldError.amount_due && (
              <p className="mt-1 text-xs text-red-600">{invoiceFieldError.amount_due}</p>
            )}
          </div>
          <div className="md:col-span-2 flex gap-2">
            <button
              className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              disabled={saving || !!invoiceDuplicate}
              type="submit"
            >
              {saving ? 'Đang tạo...' : 'Tạo hóa đơn'}
            </button>
            <button
              className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300"
              type="button"
              onClick={toggleInvoiceForm}
            >
              Hủy
            </button>
          </div>
        </form>
      )}

      {showPaymentForm && isStaff && (
        <form
          onSubmit={handlePaymentCreate}
          className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2"
        >
          {paymentFormError && (
            <div className="md:col-span-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {paymentFormError}
            </div>
          )}
          <div className="md:col-span-2">
            <label className="mb-1 block text-xs font-medium text-gray-600">Invoice</label>
            <select
              className={`w-full rounded-lg border px-3 py-2 ${
                paymentFieldError.invoice_id ? 'border-red-500 bg-red-50' : 'border-gray-200'
              }`}
              value={paymentForm.invoice_id}
              onChange={(e) => {
                const newId = e.target.value;
                setPaymentFieldError((prev) => ({ ...prev, invoice_id: '', amount_paid: '' }));
                setPaymentForm((prev) => {
                  if (!newId) {
                    return { ...prev, invoice_id: '', amount_paid: '' };
                  }
                  const inv = invoices.find((i) => String(i.id) === String(newId));
                  const remaining = inv
                    ? Math.max(0, Number(inv.amount_due || 0) - Number(inv.amount_paid || 0))
                    : 0;
                  return {
                    ...prev,
                    invoice_id: newId,
                    amount_paid: prev.amount_paid === '' ? String(remaining) : prev.amount_paid,
                  };
                });
              }}
              required
            >
              <option value="">Chọn invoice</option>
              {invoices
                .filter((item) => item.status !== 'CANCELED')
                .map((item) => {
                  const remaining = Math.max(
                    0,
                    Number(item.amount_due || 0) - Number(item.amount_paid || 0),
                  );
                  const settled =
                    remaining === 0 ? ' (đã đủ)' : ` (còn nợ ${formatCurrency(remaining)})`;
                  return (
                    <option key={item.id} value={item.id} disabled={remaining === 0}>
                      Invoice #{item.id} - {classMap[item.class_id]?.code || `Class #${item.class_id}`}
                      {settled}
                    </option>
                  );
                })}
            </select>
            {paymentFieldError.invoice_id && (
              <p className="mt-1 text-xs text-red-600">{paymentFieldError.invoice_id}</p>
            )}
          </div>
          {selectedInvoice && (
            <div className="md:col-span-2 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span>
                  Lớp:{' '}
                  <span className="font-semibold">
                    {classMap[selectedInvoice.class_id]?.code || `Class #${selectedInvoice.class_id}`}
                  </span>
                </span>
                <span className="text-gray-600">
                  Kỳ: {formatDate(selectedInvoice.period_start)} →{' '}
                  {formatDate(selectedInvoice.period_end)}
                </span>
              </div>
              <div className="mt-1 flex flex-wrap items-center justify-between gap-2">
                <span>
                  Phải thu:{' '}
                  <span className="font-semibold">{formatCurrency(selectedInvoice.amount_due)}</span>
                </span>
                <span>
                  Đã thu: <span className="font-semibold">{formatCurrency(selectedInvoice.amount_paid)}</span>
                </span>
                <span className="font-semibold text-red-600">
                  Còn nợ: {formatCurrency(selectedRemaining)}
                </span>
              </div>
            </div>
          )}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Phương thức</label>
            <select
              className="w-full rounded-lg border border-gray-200 px-3 py-2"
              value={paymentForm.payment_method}
              onChange={(e) =>
                setPaymentForm((prev) => ({ ...prev, payment_method: e.target.value }))
              }
            >
              {PAYMENT_METHOD_KEYS.map((key) => (
                <option key={key} value={key}>
                  {PAYMENT_METHOD_LABELS[key]} ({key})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Số tiền thanh toán</label>
            <input
              className={`w-full rounded-lg border px-3 py-2 ${
                paymentOverpay ? 'border-red-500 bg-red-50' : 'border-gray-200'
              }`}
              type="number"
              placeholder="Số tiền thanh toán"
              value={paymentForm.amount_paid}
              max={selectedRemaining || undefined}
              onChange={(e) => {
                setPaymentFieldError((prev) => ({ ...prev, amount_paid: '' }));
                setPaymentForm((prev) => ({ ...prev, amount_paid: e.target.value }));
              }}
              required
            />
            {selectedInvoice && (
              <div className={`mt-1 text-xs ${paymentOverpay ? 'text-red-600' : 'text-gray-500'}`}>
                {paymentOverpay
                  ? `Vượt còn nợ ${formatCurrency(paymentAmount - selectedRemaining)}`
                  : `Tối đa: ${formatCurrency(selectedRemaining)}`}
              </div>
            )}
            {paymentFieldError.amount_paid && (
              <p className="mt-1 text-xs text-red-600">{paymentFieldError.amount_paid}</p>
            )}
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-xs font-medium text-gray-600">Ghi chú</label>
            <input
              className="w-full rounded-lg border border-gray-200 px-3 py-2"
              placeholder="Ghi chú (tuỳ chọn)"
              value={paymentForm.note}
              onChange={(e) => setPaymentForm((prev) => ({ ...prev, note: e.target.value }))}
            />
          </div>
          <div className="md:col-span-2 flex gap-2">
            <button
              className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              disabled={saving || paymentInvalid}
              type="submit"
            >
              {saving ? 'Đang lưu...' : 'Ghi nhận thanh toán'}
            </button>
            <button
              className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300"
              type="button"
              onClick={togglePaymentForm}
            >
              Hủy
            </button>
          </div>
        </form>
      )}

      {activeTab === 'invoices' ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <input
              className="w-full max-w-sm rounded-lg border border-gray-200 px-3 py-2 text-sm"
              placeholder="Tìm theo mã lớp, ID, trạng thái..."
              value={invoiceSearch}
              onChange={(e) => setInvoiceSearch(e.target.value)}
            />
            <div className="text-xs text-gray-500">
              Hiển thị {sortedInvoices.length}/{invoices.length}
            </div>
          </div>
          <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <Th
                    label="Invoice"
                    sortKey="id"
                    current={invoiceSort}
                    onToggle={() => setInvoiceSort(toggleSort('id', invoiceSort))}
                  />
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Lớp</th>
                  <Th
                    label="Kỳ"
                    sortKey="period_start"
                    current={invoiceSort}
                    onToggle={() => setInvoiceSort(toggleSort('period_start', invoiceSort))}
                  />
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                    Buổi & Phí
                  </th>
                  <Th
                    label="Phải thu"
                    sortKey="amount_due"
                    current={invoiceSort}
                    onToggle={() => setInvoiceSort(toggleSort('amount_due', invoiceSort))}
                  />
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                    Đã thu / Còn nợ
                  </th>
                  <Th
                    label="Trạng thái"
                    sortKey="status"
                    current={invoiceSort}
                    onToggle={() => setInvoiceSort(toggleSort('status', invoiceSort))}
                  />
                  {isStaff && (
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                      Thao tác
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {sortedInvoices.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">#{item.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {classMap[item.class_id]?.code || `Class #${item.class_id}`}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {formatDate(item.period_start)} → {formatDate(item.period_end)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      <div>{item.completed_sessions ?? 0} buổi</div>
                      <div className="text-xs text-gray-400">
                        {formatCurrency(item.tuition_fee_per_session)}/buổi
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {formatCurrency(item.amount_due)}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="text-gray-700">{formatCurrency(item.amount_paid)}</div>
                      <div className="text-xs font-medium text-red-600">
                        Còn nợ: {formatCurrency(Math.max(0, Number(item.amount_due || 0) - Number(item.amount_paid || 0)))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <StatusBadge status={item.status} variant="invoice" />
                    </td>
                    {isStaff && (
                      <td className="px-4 py-3 text-sm">
                        {item.status !== 'CANCELED' && (
                          <button
                            className="text-red-600 hover:text-red-800"
                            onClick={() =>
                              setPendingCancel({ type: 'invoice', id: item.id, loading: false })
                            }
                          >
                            Hủy hóa đơn
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
            {sortedInvoices.length === 0 && (
              <div className="p-6 text-center text-sm text-gray-400">
                {invoices.length === 0 ? 'Chưa có hóa đơn nào.' : 'Không có hóa đơn khớp bộ lọc.'}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <input
              className="w-full max-w-sm rounded-lg border border-gray-200 px-3 py-2 text-sm"
              placeholder="Tìm theo mã lớp, ID, trạng thái..."
              value={paymentSearch}
              onChange={(e) => setPaymentSearch(e.target.value)}
            />
            <div className="text-xs text-gray-500">
              Hiển thị {sortedPayments.length}/{payments.length}
            </div>
          </div>
          <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <Th
                    label="Payment"
                    sortKey="id"
                    current={paymentSort}
                    onToggle={() => setPaymentSort(toggleSort('id', paymentSort))}
                  />
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Lớp</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Kỳ</th>
                  <Th
                    label="Số tiền"
                    sortKey="amount_paid"
                    current={paymentSort}
                    onToggle={() => setPaymentSort(toggleSort('amount_paid', paymentSort))}
                  />
                  <Th
                    label="Phương thức"
                    sortKey="payment_method"
                    current={paymentSort}
                    onToggle={() => setPaymentSort(toggleSort('payment_method', paymentSort))}
                  />
                  <Th
                    label="Trạng thái"
                    sortKey="status"
                    current={paymentSort}
                    onToggle={() => setPaymentSort(toggleSort('status', paymentSort))}
                  />
                  {isStaff && (
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                      Thao tác
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {sortedPayments.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">#{item.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {item.className || classMap[item.class_id]?.code || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{item.period || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {formatCurrency(item.amount_paid ?? item.amount)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {PAYMENT_METHOD_LABELS[item.payment_method] || item.payment_method}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <StatusBadge status={item.status} variant="payment" />
                      {item.invoice_status && (
                        <div className="mt-1 text-xs text-gray-500">
                          Invoice: {invoiceStatusLabel(item.invoice_status)}
                        </div>
                      )}
                    </td>
                    {isStaff && (
                      <td className="px-4 py-3 text-sm">
                        {item.status !== 'CANCELED' && (
                          <button
                            className="text-red-600 hover:text-red-800"
                            onClick={() =>
                              setPendingCancel({ type: 'payment', id: item.id, loading: false })
                            }
                          >
                            Hủy payment
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
            {sortedPayments.length === 0 && (
              <div className="p-6 text-center text-sm text-gray-400">
                {payments.length === 0 ? 'Chưa có thanh toán nào.' : 'Không có thanh toán khớp bộ lọc.'}
              </div>
            )}
          </div>
        </div>
      )}

      <ConfirmDialog
        open={!!pendingCancel}
        title={
          pendingCancel?.type === 'invoice'
            ? `Hủy hóa đơn #${pendingCancel?.id}?`
            : `Hủy thanh toán #${pendingCancel?.id}?`
        }
        message="Hành động này không thể hoàn tác. Vui lòng xác nhận."
        confirmText={pendingCancel?.type === 'invoice' ? 'Hủy hóa đơn' : 'Hủy thanh toán'}
        danger
        loading={!!pendingCancel?.loading}
        onConfirm={performCancel}
        onClose={() => setPendingCancel(null)}
      />
    </div>
  );
}

function Th({ label, sortKey, current, onToggle }) {
  const active = current.key === sortKey;
  const arrow = !active ? '↕' : current.dir === 'asc' ? '↑' : '↓';
  return (
    <th
      className="cursor-pointer select-none px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500 hover:text-gray-700"
      onClick={onToggle}
    >
      <span className="inline-flex items-center gap-1">
        <span>{label}</span>
        <span className={`text-xs ${active ? 'text-blue-600' : 'text-gray-300'}`}>{arrow}</span>
      </span>
    </th>
  );
}
