import api from "./api";

const UserService = {
  getUsers: async () => {
    const response = await api.get("/users/");
    return response.data;
  },

  getUserById: async (id) => {
    const response = await api.get(`/users/${id}/`);
    return response.data;
  },

  createUser: async (userData) => {
    const response = await api.post("/users/", userData);
    return response.data;
  },

  updateUser: async (id, userData) => {
    const response = await api.put(`/users/${id}/`, userData);
    return response.data;
  },

  deleteUser: async (id) => {
    const response = await api.delete(`/users/${id}/`);
    return response.data;
  },
};

export default UserService;
