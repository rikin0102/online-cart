import client from './client';

export const fetchProducts = async () => {
  const response = await client.get('/products');
  return response.data;
};
