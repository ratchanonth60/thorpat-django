import React, { createContext, useState, useContext, useEffect } from 'react';
import AuthService from '../../../shared/src/api/auth';

// 1. Create Context
const AuthContext = createContext(null);

// 2. Create Provider Component
export const AuthProvider = ({ children }) => {
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));

  useEffect(() => {
    const handleStorageChange = () => {
      setAccessToken(localStorage.getItem('access_token'));
      setRefreshToken(localStorage.getItem('refresh_token'));
    };

    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const login = async (username, password) => {
    try {
      const data = await AuthService.login(username, password);
      setAccessToken(data.access);
      setRefreshToken(data.refresh);
      return data;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const logout = () => {
    AuthService.logout();
    setAccessToken(null);
    setRefreshToken(null);
  };

  const value = {
    accessToken,
    refreshToken,
    isLoggedIn: !!accessToken, // Check if access token exists
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 3. Create Custom Hook for easy consumption
export const useAuth = () => {
  return useContext(AuthContext);
};
