export const DAY_LABELS = {
  1: 'Thứ 2',
  2: 'Thứ 3',
  3: 'Thứ 4',
  4: 'Thứ 5',
  5: 'Thứ 6',
  6: 'Thứ 7',
  7: 'Chủ nhật',
};

export function formatDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString('vi-VN');
}

export function formatDateTime(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return `${date.toLocaleDateString('vi-VN')} ${date.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
  })}`;
}

export function formatCurrency(value) {
  const number = Number(value || 0);
  return `${number.toLocaleString('vi-VN')}đ`;
}

export function formatTime(value) {
  if (!value) return '-';
  return String(value).slice(0, 5);
}

export const learningRequestStatusLabel = (status) => ({
  PENDING: 'Chờ xử lý',
  ASSIGNED: 'Đã phân công',
  CANCELED: 'Đã hủy',
}[status] || status);

export const classStatusLabel = (status) => ({
  ACTIVE: 'Đang diễn ra',
  PAUSED: 'Tạm dừng',
  COMPLETED: 'Hoàn thành',
  CANCELED: 'Đã hủy',
}[status] || status);

export const invoiceStatusLabel = (status) => ({
  PAID: 'Đã thanh toán',
  UNPAID: 'Chưa thanh toán',
  PARTIALLY_PAID: 'Thanh toán một phần',
  OVERDUE: 'Quá hạn',
  CANCELED: 'Đã hủy',
}[status] || status);

export const paymentStatusLabel = (status) => ({
  SUCCESS: 'Thành công',
  CANCELED: 'Đã hủy',
  REFUNDED: 'Đã hoàn tiền',
}[status] || status);

export const PAYMENT_METHOD_LABELS = {
  BANK_TRANSFER: 'Chuyển khoản',
  CASH: 'Tiền mặt',
  MOMO: 'Ví MoMo',
  VNPAY: 'VNPay',
};

export const PAYMENT_METHOD_KEYS = ['BANK_TRANSFER', 'CASH', 'MOMO', 'VNPAY'];
