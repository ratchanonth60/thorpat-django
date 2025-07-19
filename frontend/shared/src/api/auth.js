import api from './api';

const AuthService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login/', { username, password });
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  requestPasswordReset: async (email) => {
    const response = await api.post('/auth/password-reset/', { email });
    return response.data;
  },

  confirmPasswordReset: async (uidb64, token, new_password1, new_password2) => {
    const response = await api.post('/auth/password-reset-confirm/', {
      uidb64,
      token,
      new_password1,
      new_password2,
    });
    return response.data;
  },
};

export default AuthService;