import api from "./api";

const ProductService = {
  getProducts: async () => {
    const response = await api.get("/catalogue/products/");
    return response.data;
  },

  getProductById: async (id) => {
    const response = await api.get(`/catalogue/products/${id}/`);
    return response.data;
  },

  createProduct: async (productData) => {
    const response = await api.post("/catalogue/products/", productData);
    return response.data;
  },

  updateProduct: async (id, productData) => {
    const response = await api.put(`/catalogue/products/${id}/`, productData);
    return response.data;
  },

  deleteProduct: async (id) => {
    const response = await api.delete(`/catalogue/products/${id}/`);
    return response.data;
  },
};

export default ProductService;
