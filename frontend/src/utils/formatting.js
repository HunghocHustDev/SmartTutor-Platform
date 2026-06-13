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

export function learningRequestStatusLabel(status) {
  return {
    PENDING: 'Chờ xử lý',
    ASSIGNED: 'Đã phân công',
    CANCELED: 'Đã hủy',
  }[status] || status;
}

export function classStatusLabel(status) {
  return {
    ACTIVE: 'Đang diễn ra',
    PAUSED: 'Tạm dừng',
    COMPLETED: 'Hoàn thành',
    CANCELED: 'Đã hủy',
  }[status] || status;
}

export function invoiceStatusLabel(status) {
  return {
    PAID: 'Đã thanh toán',
    UNPAID: 'Chưa thanh toán',
    PARTIALLY_PAID: 'Thanh toán một phần',
    OVERDUE: 'Quá hạn',
    CANCELED: 'Đã hủy',
  }[status] || status;
}
