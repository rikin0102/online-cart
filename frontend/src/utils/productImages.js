// Curated high quality product photos mapped by specific product names and categories
export const PRODUCT_IMAGES = {
  'Wireless Mouse': '/images/products/wireless-mouse.jpg',
  'USB Keyboard': '/images/products/usb-keyboard.jpg',
  'Laptop Stand': '/images/products/laptop-stand.jpg',
  'HD Webcam': '/images/products/hd-webcam.jpg',
  'Wireless Headphones': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80',
  'Power Bank': 'https://images.unsplash.com/photo-1609592424364-db097960334a?auto=format&fit=crop&w=600&q=80',
  'Phone Stand': '/images/products/phone-stand.jpg',
  'HDMI Cable': '/images/products/hdmi-cable.jpg',
  'Mouse Pad': '/images/products/mouse-pad.jpg',
  'Desk Lamp': '/images/products/desk-lamp.jpg',
};

export const CATEGORY_FALLBACK_IMAGES = {
  audio: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80',
  peripherals: 'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=600&q=80',
  office: 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80',
  power: 'https://images.unsplash.com/photo-1609592424364-db097960334a?auto=format&fit=crop&w=600&q=80',
  cables: 'https://images.unsplash.com/photo-1558611848-73f7eb4001a1?auto=format&fit=crop&w=600&q=80',
  lighting: 'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=600&q=80',
  accessories: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=600&q=80',
};

const DEFAULT_IMAGE = 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80';

/**
 * Returns a high-res photo URL for any given product
 * @param {Object|string} product - The product object or product name string
 * @param {string} [category] - Optional category if string was passed
 * @returns {string} Image URL
 */
export const getProductImage = (product, category) => {
  if (!product) return DEFAULT_IMAGE;

  // If explicit image_url exists on product object
  if (typeof product === 'object' && product.image_url) {
    return product.image_url;
  }

  const name = typeof product === 'string' ? product : (product.name || product.product_name || '');
  const cat = (category || (typeof product === 'object' ? product.category : '') || '').toLowerCase();
  const nameLower = name.toLowerCase();

  // 1. Direct name match
  if (PRODUCT_IMAGES[name]) {
    return PRODUCT_IMAGES[name];
  }

  // 2. Partial name match
  if (nameLower.includes('mouse pad')) return PRODUCT_IMAGES['Mouse Pad'];
  if (nameLower.includes('mouse')) return PRODUCT_IMAGES['Wireless Mouse'];
  if (nameLower.includes('keyboard')) return PRODUCT_IMAGES['USB Keyboard'];
  if (nameLower.includes('headphone') || nameLower.includes('earphone') || nameLower.includes('earbuds')) {
    return PRODUCT_IMAGES['Wireless Headphones'];
  }
  if (nameLower.includes('webcam') || nameLower.includes('camera')) return PRODUCT_IMAGES['HD Webcam'];
  if (nameLower.includes('lamp') || nameLower.includes('light')) return PRODUCT_IMAGES['Desk Lamp'];
  if (nameLower.includes('laptop stand')) return PRODUCT_IMAGES['Laptop Stand'];
  if (nameLower.includes('phone stand')) return PRODUCT_IMAGES['Phone Stand'];
  if (nameLower.includes('stand')) return PRODUCT_IMAGES['Laptop Stand'];
  if (nameLower.includes('cable') || nameLower.includes('hdmi')) return PRODUCT_IMAGES['HDMI Cable'];
  if (nameLower.includes('power') || nameLower.includes('battery') || nameLower.includes('charger')) {
    return PRODUCT_IMAGES['Power Bank'];
  }

  // 3. Category match
  if (cat && CATEGORY_FALLBACK_IMAGES[cat]) {
    return CATEGORY_FALLBACK_IMAGES[cat];
  }

  return DEFAULT_IMAGE;
};
