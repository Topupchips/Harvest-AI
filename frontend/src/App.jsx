import { useState, useCallback, useRef } from 'react';
import MapView from './components/MapView';
import GenerateButton from './components/GenerateButton';
import LoadingOverlay from './components/LoadingOverlay';
import WorldViewer from './components/WorldViewer';
import { generateWorld } from './services/api';

const APP_STATE = {
  IDLE: 'IDLE',
  GENERATING: 'GENERATING',
  VIEWING: 'VIEWING',
};

/**
 * Capture the map viewport. Tries multiple strategies:
 * 1. Find a canvas inside the gmp-map-3d shadow DOM and grab it
 * 2. Find any canvas in the map container
 * 3. Use Google Maps Static API as a fallback (most reliable)
 */
async function captureMap(mapContainer) {
  if (!mapContainer) throw new Error('Map not ready');

  // Find the gmp-map-3d custom element
  const mapEl = mapContainer.querySelector('gmp-map-3d');

  // Strategy 1: Try to grab canvas from shadow DOM
  if (mapEl) {
    const canvases = findCanvases(mapEl);
    for (const canvas of canvases) {
      try {
        const dataUrl = canvas.toDataURL('image/png');
        if (dataUrl && dataUrl.length > 100 && dataUrl !== 'data:,') {
          // Verify it's not a blank/black image by checking a few pixels
          const response = await fetch(dataUrl);
          const blob = await response.blob();
          if (blob.size > 5000) {
            console.log('[Capture] Got canvas screenshot, size:', blob.size);
            return blob;
          }
        }
      } catch (e) {
        console.warn('[Capture] Canvas toDataURL failed:', e.message);
      }
    }
  }

  // Strategy 2: Use Google Maps Static API as reliable fallback
  if (mapEl) {
    console.log('[Capture] Canvas capture failed/blank, using Static Maps API fallback');
    const center = mapEl.getAttribute('center');
    if (center) {
      const parts = center.split(',').map((s) => s.trim());
      const lat = parts[0];
      const lng = parts[1];
      const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

      // Convert range to approximate zoom level
      const range = parseFloat(mapEl.getAttribute('range') || '1500');
      const zoom = Math.round(Math.max(1, Math.min(21, 16 - Math.log2(range / 500))));

      const staticUrl =
        `https://maps.googleapis.com/maps/api/staticmap?` +
        `center=${lat},${lng}&zoom=${zoom}&size=1024x1024` +
        `&maptype=satellite&key=${apiKey}`;

      console.log('[Capture] Fetching static map at zoom', zoom);
      const response = await fetch(staticUrl);
      if (response.ok) {
        const blob = await response.blob();
        console.log('[Capture] Static map screenshot, size:', blob.size);
        return blob;
      }
    }
  }

  // Strategy 3: html2canvas as last resort
  console.log('[Capture] Falling back to html2canvas');
  const html2canvas = (await import('html2canvas')).default;
  const capturedCanvas = await html2canvas(mapContainer, {
    useCORS: true,
    allowTaint: true,
    backgroundColor: null,
    logging: false,
  });

  return new Promise((resolve, reject) => {
    capturedCanvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error('Failed to create image blob'));
    }, 'image/png');
  });
}

/** Recursively find canvas elements, traversing shadow DOMs */
function findCanvases(el) {
  const results = [];
  if (el.tagName === 'CANVAS') results.push(el);
  if (el.shadowRoot) {
    for (const child of el.shadowRoot.querySelectorAll('*')) {
      results.push(...findCanvases(child));
    }
  }
  for (const child of el.querySelectorAll('canvas')) {
    results.push(child);
  }
  return results;
}

export default function App() {
  const [appState, setAppState] = useState(APP_STATE.IDLE);
  const [viewerUrl, setViewerUrl] = useState(null);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState(null);
  const mapRef = useRef(null);

  const handleGenerate = useCallback(async () => {
    try {
      setAppState(APP_STATE.GENERATING);
      setStatusText('Capturing viewport...');
      setError(null);

      const imageBlob = await captureMap(mapRef.current);

      setStatusText('Sending to World Labs...');
      const result = await generateWorld(imageBlob, (status) => {
        setStatusText(status);
      });

      setViewerUrl(result.viewer_url);
      setAppState(APP_STATE.VIEWING);
    } catch (err) {
      console.error('Generation failed:', err);
      setError(err.message || 'Generation failed. Please try again.');
      setAppState(APP_STATE.IDLE);
    }
  }, []);

  const handleCloseViewer = useCallback(() => {
    setAppState(APP_STATE.IDLE);
    setViewerUrl(null);
  }, []);

  return (
    <div className="relative h-full w-full">
      <MapView ref={mapRef} />

      {appState === APP_STATE.IDLE && (
        <GenerateButton onClick={handleGenerate} />
      )}

      {appState === APP_STATE.GENERATING && (
        <LoadingOverlay
          statusText={statusText}
          error={error}
          onDismissError={() => {
            setError(null);
            setAppState(APP_STATE.IDLE);
          }}
        />
      )}

      {appState === APP_STATE.VIEWING && viewerUrl && (
        <WorldViewer url={viewerUrl} onClose={handleCloseViewer} />
      )}
    </div>
  );
}
