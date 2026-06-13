import React, { useEffect, useMemo, useState } from 'react';
import {
  createInvoice,
  createPayment,
  deleteInvoice,
  deletePayment,
  listClasses,
  listInvoices,
  listPayments,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { formatCurrency, formatDate, invoiceStatusLabel } from '../utils/formatting';

const emptyInvoice = {
  class_id: '',
  period_start: '',
  period_end: '',
  completed_sessions: '',
  tuition_fee_per_session: '',
  amount_due: '',
  status: 'UNPAID',
};

const emptyPayment = {
  invoice_id: '',
  amount_paid: '',
  payment_method: 'BANK_TRANSFER',
  note: '',
};

export default function FinancePage() {
  const { user } = useAuth();
  const isStaff = user?.role === 'staff';
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

  useEffect(() => {
    if (!user) return;
    let active = true;
    const filters = user.role === 'student' ? { student_id: user.id } : {};
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
  }, [user]);

  const classMap = useMemo(() => Object.fromEntries(classes.map((item) => [item.id, item])), [classes]);

  const handleInvoiceCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        class_id: Number(invoiceForm.class_id),
        period_start: invoiceForm.period_start,
        period_end: invoiceForm.period_end,
        completed_sessions: Number(invoiceForm.completed_sessions || 0),
        tuition_fee_per_session: Number(invoiceForm.tuition_fee_per_session || 0),
        amount_due: Number(invoiceForm.amount_due || 0),
        amount_paid: 0,
        status: invoiceForm.status,
      };
      const created = await createInvoice(payload);
      setInvoices((prev) => [created, ...prev]);
      setInvoiceForm(emptyInvoice);
      setShowInvoiceForm(false);
    } catch (err) {
      setError(err?.message || 'Không tạo được hóa đơn');
    } finally {
      setSaving(false);
    }
  };

  const handlePaymentCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const created = await createPayment({
        invoice_id: Number(paymentForm.invoice_id),
        amount_paid: Number(paymentForm.amount_paid || 0),
        payment_method: paymentForm.payment_method,
        note: paymentForm.note || null,
        staff_id: isStaff ? user.id : null,
      });
      setPayments((prev) => [created, ...prev]);
      setPaymentForm(emptyPayment);
      setShowPaymentForm(false);
      const freshInvoices = await listInvoices();
      setInvoices(Array.isArray(freshInvoices) ? freshInvoices : []);
    } catch (err) {
      setError(err?.message || 'Không ghi nhận được thanh toán');
    } finally {
      setSaving(false);
    }
  };

  const handleCancelInvoice = async (id) => {
    if (!window.confirm('Bạn có muốn hủy hóa đơn này không?')) return;
    try {
      await deleteInvoice(id);
      setInvoices((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'CANCELED' } : item)));
    } catch (err) {
      setError(err?.message || 'Không hủy được hóa đơn');
    }
  };

  const handleCancelPayment = async (id) => {
    if (!window.confirm('Bạn có muốn hủy thanh toán này không?')) return;
    try {
      await deletePayment(id);
      const freshPayments = await listPayments(user?.role === 'student' ? { student_id: user.id } : {});
      const freshInvoices = await listInvoices();
      setPayments(Array.isArray(freshPayments) ? freshPayments : []);
      setInvoices(Array.isArray(freshInvoices) ? freshInvoices : []);
    } catch (err) {
      setError(err?.message || 'Không hủy được thanh toán');
    }
  };

  if (!user) {
    return <div className="rounded-lg bg-white p-6 shadow">Vui lòng đăng nhập để xem học phí.</div>;
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow">Đang tải dữ liệu tài chính...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{isStaff ? 'Quản lý học phí và thanh toán' : 'Học phí của tôi'}</h1>
          <p className="text-sm text-gray-500">Theo dõi invoice snapshot và payment thực tế.</p>
        </div>
        {isStaff && (
          <div className="flex gap-2">
            <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" onClick={() => setShowInvoiceForm((prev) => !prev)}>
              {showInvoiceForm ? 'Đóng form hóa đơn' : 'Tạo hóa đơn'}
            </button>
            <button className="rounded-lg bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700" onClick={() => setShowPaymentForm((prev) => !prev)}>
              {showPaymentForm ? 'Đóng form thanh toán' : 'Ghi nhận thanh toán'}
            </button>
          </div>
        )}
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="flex gap-2">
        <button className={`rounded-lg px-4 py-2 ${activeTab === 'invoices' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`} onClick={() => setActiveTab('invoices')}>Hóa đơn</button>
        <button className={`rounded-lg px-4 py-2 ${activeTab === 'payments' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`} onClick={() => setActiveTab('payments')}>Thanh toán</button>
      </div>

      {showInvoiceForm && isStaff && (
        <form onSubmit={handleInvoiceCreate} className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2">
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={invoiceForm.class_id} onChange={(e) => setInvoiceForm((prev) => ({ ...prev, class_id: e.target.value }))} required>
            <option value="">Chọn lớp</option>
            {classes.map((item) => (
              <option key={item.id} value={item.id}>{item.code} - {item.subject} - {item.student}</option>
            ))}
          </select>
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={invoiceForm.status} onChange={(e) => setInvoiceForm((prev) => ({ ...prev, status: e.target.value }))}>
            <option value="UNPAID">UNPAID</option>
            <option value="PARTIALLY_PAID">PARTIALLY_PAID</option>
            <option value="PAID">PAID</option>
          </select>
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="date" value={invoiceForm.period_start} onChange={(e) => setInvoiceForm((prev) => ({ ...prev, period_start: e.target.value }))} required />
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="date" value={invoiceForm.period_end} onChange={(e) => setInvoiceForm((prev) => ({ ...prev, period_end: e.target.value }))} required />
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="number" placeholder="Số buổi hoàn thành" value={invoiceForm.completed_sessions} onChange={(e) => setInvoiceForm((prev) => ({ ...prev, completed_sessions: e.target.value }))} required />
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="number" placeholder="Học phí / buổi" value={invoiceForm.tuition_fee_per_session} onChange={(e) => setInvoiceForm((prev) => ({ ...prev, tuition_fee_per_session: e.target.value }))} required />
          <input className="rounded-lg border border-gray-200 px-3 py-2 md:col-span-2" type="number" placeholder="Tổng tiền phải thu" value={invoiceForm.amount_due} onChange={(e) => setInvoiceForm((prev) => ({ ...prev, amount_due: e.target.value }))} required />
          <div className="md:col-span-2 flex gap-2">
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">{saving ? 'Đang tạo...' : 'Tạo hóa đơn'}</button>
            <button className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300" type="button" onClick={() => setShowInvoiceForm(false)}>Hủy</button>
          </div>
        </form>
      )}

      {showPaymentForm && isStaff && (
        <form onSubmit={handlePaymentCreate} className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2">
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={paymentForm.invoice_id} onChange={(e) => setPaymentForm((prev) => ({ ...prev, invoice_id: e.target.value }))} required>
            <option value="">Chọn invoice</option>
            {invoices.filter((item) => item.status !== 'CANCELED').map((item) => (
              <option key={item.id} value={item.id}>Invoice #{item.id} - {classMap[item.class_id]?.code || `Class #${item.class_id}`}</option>
            ))}
          </select>
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={paymentForm.payment_method} onChange={(e) => setPaymentForm((prev) => ({ ...prev, payment_method: e.target.value }))}>
            <option value="BANK_TRANSFER">BANK_TRANSFER</option>
            <option value="CASH">CASH</option>
          </select>
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="number" placeholder="Số tiền thanh toán" value={paymentForm.amount_paid} onChange={(e) => setPaymentForm((prev) => ({ ...prev, amount_paid: e.target.value }))} required />
          <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Ghi chú" value={paymentForm.note} onChange={(e) => setPaymentForm((prev) => ({ ...prev, note: e.target.value }))} />
          <div className="md:col-span-2 flex gap-2">
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">{saving ? 'Đang lưu...' : 'Ghi nhận thanh toán'}</button>
            <button className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300" type="button" onClick={() => setShowPaymentForm(false)}>Hủy</button>
          </div>
        </form>
      )}

      {activeTab === 'invoices' ? (
        <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Invoice</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Lớp</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Kỳ</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Số tiền</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Trạng thái</th>
                {isStaff && <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Thao tác</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {invoices.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">#{item.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{classMap[item.class_id]?.code || `Class #${item.class_id}`}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{formatDate(item.period_start)} - {formatDate(item.period_end)}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    <div>Phải thu: {formatCurrency(item.amount_due)}</div>
                    <div>Đã thu: {formatCurrency(item.amount_paid)}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{invoiceStatusLabel(item.status)}</td>
                  {isStaff && (
                    <td className="px-4 py-3 text-sm">
                      <button className="text-red-600 hover:text-red-800" onClick={() => handleCancelInvoice(item.id)}>Hủy hóa đơn</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {invoices.length === 0 && <div className="p-6 text-center text-sm text-gray-400">Chưa có hóa đơn nào.</div>}
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Payment</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Lớp</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Kỳ</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Số tiền</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Trạng thái</th>
                {isStaff && <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Thao tác</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {payments.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">#{item.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.className || classMap[item.class_id]?.code || '-'}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.period || '-'}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.amount}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    <div>{item.status}</div>
                    <div className="text-xs text-gray-500">{item.invoice_status || '-'}</div>
                  </td>
                  {isStaff && (
                    <td className="px-4 py-3 text-sm">
                      <button className="text-red-600 hover:text-red-800" onClick={() => handleCancelPayment(item.id)}>Hủy payment</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {payments.length === 0 && <div className="p-6 text-center text-sm text-gray-400">Chưa có thanh toán nào.</div>}
        </div>
      )}
    </div>
  );
}
