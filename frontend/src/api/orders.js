import client from './client';

export const submitOrder = async () => {
  const response = await client.post('/orders/submit');
  return response.data;
};
