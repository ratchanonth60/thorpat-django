import React from 'react';
import LoginForm from '../components/auth/LoginForm';
import LoginImage from '../components/auth/LoginImage';

const LoginScreen = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 font-sans">
      <div className="flex w-full max-w-4xl mx-auto overflow-hidden bg-white rounded-lg shadow-lg">
        <LoginImage />
        <div className="flex items-center justify-center w-full lg:w-1/2">
          <LoginForm />
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;