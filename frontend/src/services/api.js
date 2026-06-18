const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

function getStoredToken() {
  try {
    const raw = localStorage.getItem('smarttutor_user') || localStorage.getItem('user');
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    return parsed?.token || null;
  } catch {
    return null;
  }
}

async function request(path, options = {}) {
  const token = options.token || getStoredToken();
  const { token: _tokenOverride, ...fetchOptions } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(fetchOptions.headers || {}),
    },
    ...fetchOptions,
  });

  let data = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    const message = data && typeof data === 'object' ? data.detail || data.message : data;
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return data;
}

const buildQueryString = (params = {}) => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.set(key, value);
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
};

export const login = (payload) => request('/auth/login', {
  method: 'POST',
  body: JSON.stringify(payload),
});

export const register = (payload) => request('/auth/register', {
  method: 'POST',
  body: JSON.stringify(payload),
});

export const getDashboardSummary = () => request('/dashboard/summary');

export const listStudents = (filters = {}, options = {}) => request(`/students${buildQueryString(filters)}`, options);
export const createStudent = (payload) => request('/students', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateStudent = (id, payload) => request(`/students/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteStudent = (id) => request(`/students/${id}`, { method: 'DELETE' });

export const listTutors = (filters = {}, options = {}) => request(`/tutors${buildQueryString(filters)}`, options);
export const createTutor = (payload) => request('/tutors', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateTutor = (id, payload) => request(`/tutors/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteTutor = (id) => request(`/tutors/${id}`, { method: 'DELETE' });
export const listTutorCapabilities = (tutorId) => request(`/tutors/${tutorId}/capabilities`);
export const addTutorCapability = (tutorId, payload) => request(`/tutors/${tutorId}/capabilities`, {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const deleteTutorCapability = (tutorId, capabilityId) => request(`/tutors/${tutorId}/capabilities/${capabilityId}`, {
  method: 'DELETE',
});
export const listTutorAvailability = (tutorId) => request(`/tutors/${tutorId}/availability`);
export const createTutorAvailability = (tutorId, payload) => request(`/tutors/${tutorId}/availability`, {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateTutorAvailability = (tutorId, availabilityId, payload) => request(`/tutors/${tutorId}/availability/${availabilityId}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteTutorAvailability = (tutorId, availabilityId) => request(`/tutors/${tutorId}/availability/${availabilityId}`, {
  method: 'DELETE',
});

export const listSubjects = (filters = {}) => request(`/subjects${buildQueryString(filters)}`);
export const createSubject = (payload) => request('/subjects', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateSubject = (id, payload) => request(`/subjects/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteSubject = (id) => request(`/subjects/${id}`, { method: 'DELETE' });

export const listClasses = (filters = {}) => request(`/classes${buildQueryString(filters)}`);
export const createClass = (payload) => request('/classes', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateClass = (id, payload) => request(`/classes/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteClass = (id) => request(`/classes/${id}`, { method: 'DELETE' });
export const getClassTuitionSummary = (classId) => request(`/classes/${classId}/tuition-summary`);
export const getClassInvoicePeriod = (classId) => request(`/classes/${classId}/invoice-period`);

export const listLearningRequests = (filters = {}) => request(`/learning-requests${buildQueryString(filters)}`);
export const createLearningRequest = (payload) => request('/learning-requests', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateLearningRequest = (id, payload) => request(`/learning-requests/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteLearningRequest = (id) => request(`/learning-requests/${id}`, { method: 'DELETE' });

export const getSuggestedTutors = (requestId) => request(`/learning-requests/${requestId}/suggested-tutors`);

export const listSessions = (filters = {}) => request(`/sessions${buildQueryString(filters)}`);
export const createSession = (payload) => request('/sessions', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateSession = (id, payload) => request(`/sessions/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const updateSessionStatus = (id, payload) => request(`/sessions/${id}/status`, {
  method: 'PATCH',
  body: JSON.stringify(payload),
});
export const deleteSession = (id) => request(`/sessions/${id}`, { method: 'DELETE' });
export const previewSessionsFromSchedules = (payload) => request('/sessions/preview-from-schedules', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const generateSessionsFromSchedules = (payload) => request('/sessions/generate-from-schedules', {
  method: 'POST',
  body: JSON.stringify(payload),
});

export const listAssignments = (filters = {}) => request(`/assignments${buildQueryString(filters)}`);
export const createAssignment = (payload) => request('/assignments', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateAssignment = (id, payload) => request(`/assignments/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const cancelAssignment = (id) => request(`/assignments/${id}`, { method: 'DELETE' });

export const listSchedules = (filters = {}) => request(`/schedules${buildQueryString(filters)}`);
export const createSchedule = (payload) => request('/schedules', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateSchedule = (id, payload) => request(`/schedules/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteSchedule = (id) => request(`/schedules/${id}`, { method: 'DELETE' });

export const listInvoices = (filters = {}) => request(`/invoices${buildQueryString(filters)}`);
export const createInvoice = (payload) => request('/invoices', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updateInvoice = (id, payload) => request(`/invoices/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deleteInvoice = (id) => request(`/invoices/${id}`, { method: 'DELETE' });

export const listPayments = (filters = {}) => request(`/payments${buildQueryString(filters)}`);
export const createPayment = (payload) => request('/payments', {
  method: 'POST',
  body: JSON.stringify(payload),
});
export const updatePayment = (id, payload) => request(`/payments/${id}`, {
  method: 'PUT',
  body: JSON.stringify(payload),
});
export const deletePayment = (id) => request(`/payments/${id}`, { method: 'DELETE' });

export const api = {
  request,
  login,
  register,
  getDashboardSummary,
  listStudents,
  createStudent,
  updateStudent,
  deleteStudent,
  listTutors,
  createTutor,
  updateTutor,
  deleteTutor,
  listTutorCapabilities,
  addTutorCapability,
  deleteTutorCapability,
  listTutorAvailability,
  createTutorAvailability,
  updateTutorAvailability,
  deleteTutorAvailability,
  listSubjects,
  createSubject,
  updateSubject,
  deleteSubject,
  listClasses,
  createClass,
  updateClass,
  deleteClass,
  getClassTuitionSummary,
  getClassInvoicePeriod,
  listLearningRequests,
  createLearningRequest,
  updateLearningRequest,
  deleteLearningRequest,
  listSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  listSessions,
  createSession,
  updateSession,
  updateSessionStatus,
  deleteSession,
  listAssignments,
  createAssignment,
  updateAssignment,
  cancelAssignment,
  listInvoices,
  createInvoice,
  updateInvoice,
  deleteInvoice,
  listPayments,
  createPayment,
  updatePayment,
  deletePayment,
};
