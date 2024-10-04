import axios from 'axios';

const API_URL = '/api/';

export const uploadMenu = (file) => {
  const formData = new FormData();
  formData.append('menuImage', file);
  return axios.post(`${API_URL}upload`, formData);
};

export const getMenus = () => {
  return axios.get(`${API_URL}menus`);
};