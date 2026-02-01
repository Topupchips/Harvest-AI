import axios from 'axios';

const API_BASE = '/api';

/**
 * Use GPT-4o to describe a product image in detail.
 * Returns a text description suitable for 3D world generation.
 *
 * @param {Blob} imageBlob - Product image blob
 * @returns {Promise<string>} - Detailed product description
 */
export async function describeProductImage(imageBlob) {
  const formData = new FormData();
  formData.append('image', imageBlob, 'product.png');

  const { data } = await axios.post(`${API_BASE}/describe-image`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000, // 60 second timeout for GPT-4o
  });

  return data.description;
}

/**
 * Remove background from a product image.
 * Returns the image with transparent background.
 *
 * @param {Blob} imageBlob - Product image blob
 * @returns {Promise<Blob>} - Image with transparent background
 */
export async function removeBackground(imageBlob) {
  const formData = new FormData();
  formData.append('image', imageBlob, 'product.png');

  const response = await axios.post(`${API_BASE}/remove-background`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    responseType: 'blob',
    timeout: 60000,
  });

  return response.data;
}

/**
 * Send captured map image to backend, which handles the full World Labs flow.
 * Returns { viewer_url, world_id, thumbnail_url, splat_urls }
 *
 * @param {Blob} imageBlob - PNG image blob from canvas capture
 * @param {function} onStatusUpdate - Callback for status text updates
 */
export async function generateWorld(imageBlob, onStatusUpdate) {
  const formData = new FormData();
  formData.append('image', imageBlob, 'viewport.png');

  onStatusUpdate?.('Uploading image...');

  const { data } = await axios.post(`${API_BASE}/generate-world`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000, // 10-minute timeout for Marble 0.1-plus generation
  });

  if (data.viewer_url) {
    onStatusUpdate?.('World ready!');
    return data;
  }

  throw new Error(data.detail || 'Unexpected response from server');
}

/**
 * Send multiple captured satellite images to backend for multi-image world generation.
 * Returns { viewer_url, world_id, thumbnail_url, splat_urls }
 *
 * @param {Array<{blob: Blob, azimuth: number}>} images - Array of image blobs with their azimuth angles
 * @param {string} textPrompt - Description of the location for World Labs
 * @param {function} onStatusUpdate - Callback for status text updates
 * @param {Object} [productOptions] - Optional product image options
 * @param {Blob} [productOptions.image] - Product image blob to composite
 * @param {string} [productOptions.position] - Position for product ("center", "bottom-center", "left", "right")
 * @param {number} [productOptions.scale] - Size of product relative to background (0.0-1.0)
 */
export async function generateWorldMulti(images, textPrompt, onStatusUpdate, productOptions = null) {
  const formData = new FormData();

  // Collect azimuths as an array for JSON encoding
  const azimuths = [];

  // Append each image (backend expects field name 'images' for List[UploadFile])
  images.forEach((image) => {
    formData.append('images', image.blob, `view_${image.azimuth}.png`);
    azimuths.push(image.azimuth);
  });

  // Send azimuths as JSON string (backend expects this format)
  formData.append('azimuths', JSON.stringify(azimuths));

  // Include the text prompt
  if (textPrompt) {
    formData.append('text_prompt', textPrompt);
  }

  // Include product image if provided
  if (productOptions?.image) {
    formData.append('product_image', productOptions.image, 'product.png');
    if (productOptions.position) {
      formData.append('product_position', productOptions.position);
    }
    if (productOptions.scale !== undefined) {
      formData.append('product_scale', productOptions.scale.toString());
    }
  }

  onStatusUpdate?.('Uploading images...');

  const { data } = await axios.post(`${API_BASE}/generate-world-multi`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000, // 10-minute timeout for Marble 0.1-plus generation
  });

  if (data.viewer_url) {
    onStatusUpdate?.('World ready!');
    return data;
  }

  throw new Error(data.detail || 'Unexpected response from server');
}

/**
 * Fetch all stored worlds from Supabase.
 * Returns array of world objects with viewer_url, world_id, thumbnail_url, etc.
 *
 * @returns {Promise<Array>} - Array of world objects
 */
export async function fetchWorlds() {
  const { data } = await axios.get(`${API_BASE}/worlds`, {
    timeout: 30000,
  });
  return data.worlds || [];
}
