import client from './client';

export const fetchCart = async () => {
  const response = await client.get('/cart');
  return response.data;
};

export const addItemToCart = async (productId, quantity = 1) => {
  const response = await client.post('/cart/items', {
    product_id: productId,
    quantity,
  });
  return response.data;
};

export const updateItemQuantity = async (productId, quantity) => {
  const response = await client.patch(`/cart/items/${productId}`, {
    quantity,
  });
  return response.data;
};

export const removeItemFromCart = async (productId) => {
  const response = await client.delete(`/cart/items/${productId}`);
  return response.data;
};
