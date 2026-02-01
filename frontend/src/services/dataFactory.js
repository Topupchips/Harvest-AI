const API_BASE = '/api';

const EVENT_TYPES = [
  'extract_start',
  'panorama_found',
  'panorama_downloaded',
  'views_extracted',
  'image_saved',
  'pipeline_complete',
  'error',
];

const DETECTION_EVENT_TYPES = [
  'detection_start',
  'candidates_found',
  'match_verified',
  'image_processed',
  'detection_complete',
  'error',
];

/**
 * Connect to the data factory extraction SSE stream.
 *
 * @param {object} worldData - World data from generate response (needs world_id or viewer_url)
 * @param {number} numViews - Number of perspective views to extract
 * @param {object} callbacks
 * @param {function} callbacks.onEvent  - (eventType, data) => void
 * @param {function} callbacks.onComplete - (data) => void
 * @param {function} callbacks.onError  - (error) => void
 * @returns {{ close: () => void }}
 */
export function startExtraction(worldData, numViews, callbacks) {
  const params = new URLSearchParams({
    num_views: String(numViews),
  });

  if (worldData.world_id) {
    params.set('world_id', worldData.world_id);
  }
  if (worldData.viewer_url) {
    params.set('viewer_url', worldData.viewer_url);
  }

  const url = `${API_BASE}/data-factory/extract?${params.toString()}`;
  const eventSource = new EventSource(url);

  EVENT_TYPES.forEach((type) => {
    eventSource.addEventListener(type, (e) => {
      const data = JSON.parse(e.data);
      callbacks.onEvent?.(type, data);

      if (type === 'pipeline_complete') {
        callbacks.onComplete?.(data);
        eventSource.close();
      }
      if (type === 'error' && data.fatal) {
        callbacks.onError?.(new Error(data.message));
        eventSource.close();
      }
    });
  });

  eventSource.onerror = () => {
    callbacks.onError?.(new Error('Connection to data factory lost'));
    eventSource.close();
  };

  return { close: () => eventSource.close() };
}

/**
 * Upload a reference image for detection.
 * @param {File} imageFile - The reference image file
 * @returns {Promise<{reference_id: string}>}
 */
export async function uploadReference(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);

  const response = await fetch(`${API_BASE}/data-factory/upload-reference`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Reference upload failed');
  }

  return response.json();
}

/**
 * Connect to the detection SSE stream.
 * @param {string} referenceId - ID from uploadReference
 * @param {string} objectClass - YOLO class name to detect
 * @param {object} callbacks
 * @param {function} callbacks.onEvent - (eventType, data) => void
 * @param {function} callbacks.onComplete - (data) => void
 * @param {function} callbacks.onError - (error) => void
 * @returns {{ close: () => void }}
 */
export function startDetection(referenceId, objectClass, callbacks) {
  const params = new URLSearchParams({
    reference_id: referenceId,
    object_class: objectClass,
  });

  const url = `${API_BASE}/data-factory/detect?${params.toString()}`;
  const eventSource = new EventSource(url);

  DETECTION_EVENT_TYPES.forEach((type) => {
    eventSource.addEventListener(type, (e) => {
      const data = JSON.parse(e.data);
      callbacks.onEvent?.(type, data);

      if (type === 'detection_complete') {
        callbacks.onComplete?.(data);
        eventSource.close();
      }
      if (type === 'error' && data.fatal) {
        callbacks.onError?.(new Error(data.message));
        eventSource.close();
      }
    });
  });

  eventSource.onerror = () => {
    callbacks.onError?.(new Error('Connection to detection pipeline lost'));
    eventSource.close();
  };

  return { close: () => eventSource.close() };
}

/**
 * Get URL for a preview image.
 */
export function getPreviewImageUrl(filename) {
  return `${API_BASE}/data-factory/preview/${encodeURIComponent(filename)}`;
}

/**
 * Get URL for an annotated image.
 */
export function getAnnotatedImageUrl(filename) {
  return `${API_BASE}/data-factory/preview/${encodeURIComponent(filename)}?annotated=true`;
}

/**
 * Get URL to download all annotated images as a zip.
 */
export function getDownloadUrl() {
  return `${API_BASE}/data-factory/download-annotated`;
}
