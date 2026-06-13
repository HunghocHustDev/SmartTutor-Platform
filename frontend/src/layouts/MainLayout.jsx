import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/Header';
import Sidebar from '../components/common/Sidebar';
import { useAuth } from '../contexts/AuthContext';

const MainLayout = () => {
  const { user } = useAuth();
  const showSidebar = user && user.role; // chỉ hiện sidebar khi đã login

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <div className="flex flex-1">
        {showSidebar && <Sidebar />}
        <main className={`flex-1 p-6 ${showSidebar ? '' : 'w-full'}`}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;