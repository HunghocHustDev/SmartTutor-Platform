import React, { createContext, useState, useContext, useEffect } from 'react';
import {
  login as loginRequest,
  register as registerRequest,
  listStudents,
  listTutors,
} from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

async function hydrateUserProfile(userData) {
  if (!userData || !userData.role || !userData.email) {
    return userData;
  }

  const requestOptions = userData.token ? { token: userData.token } : {};

  if (userData.role === 'tutor') {
    const tutors = await listTutors({ email: userData.email }, requestOptions);
    const tutor = tutors.find((item) => item.email === userData.email) || tutors[0];
    if (tutor) {
      return {
        ...userData,
        id: tutor.id ?? userData.id,
        name: tutor.full_name || userData.name,
        area: tutor.area ?? userData.area,
        experience: tutor.experience ?? userData.experience,
      };
    }
    return null;
  }

  if (userData.role === 'student') {
    const students = await listStudents({ email: userData.email }, requestOptions);
    const student = students.find((item) => item.email === userData.email) || students[0];
    if (student) {
      return {
        ...userData,
        id: student.id ?? userData.id,
        name: student.full_name || userData.name,
        area: student.area ?? userData.area,
        level: student.level ?? userData.level,
      };
    }
    return null;
  }

  if (userData.role === 'staff') {
    return userData;
  }

  return userData;
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('smarttutor_user') || localStorage.getItem('user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
        hydrateUserProfile(parsedUser)
          .then((freshUser) => {
            if (!freshUser) {
              localStorage.removeItem('smarttutor_user');
              localStorage.removeItem('user');
              setUser(null);
              return;
            }
            localStorage.setItem('smarttutor_user', JSON.stringify(freshUser));
            localStorage.setItem('user', JSON.stringify(freshUser));
            setUser(freshUser);
          })
          .catch(() => {
            localStorage.removeItem('smarttutor_user');
            localStorage.removeItem('user');
            setUser(null);
          });
      } catch {
        localStorage.removeItem('smarttutor_user');
        localStorage.removeItem('user');
      }
    }
  }, []);

  const login = (userData) => {
    localStorage.setItem('smarttutor_user', JSON.stringify(userData));
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('smarttutor_user');
    localStorage.removeItem('user');
    setUser(null);
  };

  const loginWithCredentials = async (email, password) => {
    const response = await loginRequest({ email, password });
    const hydratedUser = await hydrateUserProfile({
      ...response.user,
      token: response.access_token || response.token,
    });
    if (!hydratedUser) {
      throw new Error('Tài khoản đăng nhập không có hồ sơ hợp lệ trong hệ thống');
    }
    login(hydratedUser);
    return response;
  };

  const registerAccount = async (payload) => {
    const registered = await registerRequest(payload);
    const loginResponse = await loginRequest({
      email: payload.email,
      password: payload.password,
    });
    const hydratedUser = await hydrateUserProfile({
      ...loginResponse.user,
      token: loginResponse.access_token || loginResponse.token,
    });
    if (!hydratedUser) {
      throw new Error('Đăng ký thành công nhưng không tìm thấy hồ sơ vừa tạo trong hệ thống');
    }
    login(hydratedUser);
    return {
      registered,
      login: loginResponse,
    };
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loginWithCredentials, registerAccount }}>
      {children}
    </AuthContext.Provider>
  );
};
