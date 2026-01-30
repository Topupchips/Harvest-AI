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
