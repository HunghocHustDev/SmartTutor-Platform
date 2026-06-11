import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = (userData) => {
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  // Fake login cho test role
  const fakeLogin = (role, name) => {
    const fakeUser = { role, name, token: 'fake-jwt-token' };
    login(fakeUser);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, fakeLogin }}>
      {children}
    </AuthContext.Provider>
  );
};