import axios from 'axios';

const API_BASE = '/api';

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
    timeout: 180000, // 3-minute timeout for the full server-side flow
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
 */
export async function generateWorldMulti(images, textPrompt, onStatusUpdate) {
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

  onStatusUpdate?.('Uploading images...');

  const { data } = await axios.post(`${API_BASE}/generate-world-multi`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000, // 5-minute timeout for multi-image processing
  });

  if (data.viewer_url) {
    onStatusUpdate?.('World ready!');
    return data;
  }

  throw new Error(data.detail || 'Unexpected response from server');
}
