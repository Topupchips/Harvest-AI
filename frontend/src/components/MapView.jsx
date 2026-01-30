import { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

// San Francisco — guaranteed photorealistic 3D coverage
const DEFAULT_CENTER = { lat: 37.7950, lng: -122.4034, altitude: 200 };
const DEFAULT_RANGE = 1500;
const DEFAULT_TILT = 67;
const DEFAULT_HEADING = 330;

function loadGoogleMapsScript(apiKey) {
  return new Promise((resolve, reject) => {
    if (window.google?.maps) {
      resolve();
      return;
    }
    if (document.querySelector('script[src*="maps.googleapis.com"]')) {
      const check = setInterval(() => {
        if (window.google?.maps) { clearInterval(check); resolve(); }
      }, 100);
      return;
    }
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&v=beta&libraries=maps3d`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      const check = setInterval(() => {
        if (window.google?.maps) { clearInterval(check); resolve(); }
      }, 50);
    };
    script.onerror = () => reject(new Error('Failed to load Google Maps script'));
    document.head.appendChild(script);
  });
}

const MapView = forwardRef((_props, ref) => {
  const wrapperRef = useRef(null);
  const mapHostRef = useRef(null);
  const [status, setStatus] = useState('Initializing...');
  const [hasError, setHasError] = useState(false);

  // Expose the mapHost div (contains the gmp-map-3d element) for screenshot capture
  useImperativeHandle(ref, () => mapHostRef.current);

  useEffect(() => {
    const mapHost = mapHostRef.current;
    if (!mapHost) return;

    async function initMap() {
      if (!GOOGLE_MAPS_API_KEY) {
        throw new Error('VITE_GOOGLE_MAPS_API_KEY is not set — add it to frontend/.env');
      }

      setStatus('Loading Google Maps API...');
      await loadGoogleMapsScript(GOOGLE_MAPS_API_KEY);

      setStatus('Loading 3D library...');
      await google.maps.importLibrary('maps3d');

      setStatus('Creating 3D map...');

      const map3d = document.createElement('gmp-map-3d');
      map3d.setAttribute('center', `${DEFAULT_CENTER.lat},${DEFAULT_CENTER.lng},${DEFAULT_CENTER.altitude}`);
      map3d.setAttribute('range', String(DEFAULT_RANGE));
      map3d.setAttribute('tilt', String(DEFAULT_TILT));
      map3d.setAttribute('heading', String(DEFAULT_HEADING));
      map3d.setAttribute('mode', 'hybrid');
      map3d.style.width = '100%';
      map3d.style.height = '100%';
      map3d.style.display = 'block';

      mapHost.appendChild(map3d);
      setStatus('');
    }

    initMap().catch((err) => {
      console.error('[MapView] Init failed:', err);
      setHasError(true);
      setStatus(err.message || 'Failed to load map');
    });

    return () => {
      // Cleanup: remove any map elements on unmount
      while (mapHost.firstChild) {
        mapHost.removeChild(mapHost.firstChild);
      }
    };
  }, []);

  return (
    <div ref={wrapperRef} className="absolute inset-0 w-full h-full" style={{ zIndex: 0 }}>
      {/* Map renders here */}
      <div ref={mapHostRef} className="absolute inset-0 w-full h-full" />

      {/* Status overlay — separate from map host so it's never wiped */}
      {status && (
        <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
          <div className={`px-6 py-3 rounded-xl text-sm font-medium backdrop-blur-sm ${
            hasError ? 'bg-red-900/80 text-red-200' : 'bg-dark-800/80 text-gray-300'
          }`}>
            {status}
          </div>
        </div>
      )}
    </div>
  );
});

MapView.displayName = 'MapView';
export default MapView;
