import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
        <button
          onClick={logout}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition duration-300"
        >
          Logout
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-semibold text-gray-900 mb-6">Welcome!</h2>

          {/* Quick Links / Navigation */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Link to="/users" className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition duration-300">
              <h3 className="text-xl font-semibold text-indigo-600 mb-2">Manage Users</h3>
              <p className="text-gray-600">View, add, edit, or delete user accounts.</p>
            </Link>

            <Link to="/products" className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition duration-300">
              <h3 className="text-xl font-semibold text-indigo-600 mb-2">Manage Products</h3>
              <p className="text-gray-600">Browse and manage product listings.</p>
            </Link>

            {/* Add more links as needed */}
            <div className="block p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Reports</h3>
              <p className="text-gray-600">Access various system reports.</p>
            </div>

            <div className="block p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Settings</h3>
              <p className="text-gray-600">Configure application settings.</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white shadow-inner p-4 text-center text-gray-500 text-sm">
        © 2025 Thorpat Admin. All rights reserved.
      </footer>
    </div>
  );
};

export default Dashboard;