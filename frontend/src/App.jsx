import { useState, useCallback, useRef } from 'react';
import MapView from './components/MapView';
import LoadingOverlay from './components/LoadingOverlay';
import WorldViewer from './components/WorldViewer';
import LocationPopup from './components/LocationPopup';
import { reverseGeocode, generateLocationDescription } from './services/geocoding';
import { generateWorldMulti } from './services/api';

const APP_STATE = {
  IDLE: 'IDLE',
  LOCATION_SELECTED: 'LOCATION_SELECTED',
  GENERATING: 'GENERATING',
  VIEWING: 'VIEWING',
};

export default function App() {
  const [appState, setAppState] = useState(APP_STATE.IDLE);
  const [viewerUrl, setViewerUrl] = useState(null);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const mapRef = useRef(null);

  /**
   * Capture a single satellite image for a location.
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   * @returns {Promise<Blob>}
   */
  const captureSatelliteImage = useCallback(async (lat, lng) => {
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    const staticUrl =
      `https://maps.googleapis.com/maps/api/staticmap?` +
      `center=${lat},${lng}&zoom=18&size=1024x1024` +
      `&maptype=satellite&key=${apiKey}`;

    console.log(`[Capture] Fetching satellite view for ${lat}, ${lng}`);
    const response = await fetch(staticUrl);

    if (!response.ok) {
      throw new Error(`Failed to fetch satellite image`);
    }

    const blob = await response.blob();
    console.log(`[Capture] Got satellite image, size:`, blob.size);

    return blob;
  }, []);

  /**
   * Capture multiple Street View images at different headings from a location.
   * Uses Google Street View Static API for ground-level panoramic views.
   * @param {number} lat - Center latitude
   * @param {number} lng - Center longitude
   * @returns {Promise<Array<{blob: Blob, azimuth: number}>>}
   */
  const captureMultipleViews = useCallback(async (lat, lng) => {
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

    // Capture 4 Street View images at cardinal directions
    const views = [
      { name: 'North', heading: 0, azimuth: 0 },
      { name: 'East', heading: 90, azimuth: 90 },
      { name: 'South', heading: 180, azimuth: 180 },
      { name: 'West', heading: 270, azimuth: 270 },
    ];

    const results = [];

    for (const view of views) {
      // Street View Static API with heading parameter
      const streetViewUrl =
        `https://maps.googleapis.com/maps/api/streetview?` +
        `location=${lat},${lng}` +
        `&size=1024x1024` +
        `&heading=${view.heading}` +
        `&pitch=0` +  // Horizontal view (0 = level, negative = down, positive = up)
        `&fov=90` +   // Field of view (90° is good for capturing surroundings)
        `&key=${apiKey}`;

      console.log(`[Capture] Fetching Street View ${view.name} (heading ${view.heading}) at ${lat}, ${lng}`);
      const response = await fetch(streetViewUrl);

      if (!response.ok) {
        throw new Error(`Failed to fetch Street View for ${view.name} direction`);
      }

      const blob = await response.blob();
      console.log(`[Capture] Got ${view.name} Street View, size:`, blob.size);

      // Check if we got a valid image (Street View returns a "no imagery" placeholder if unavailable)
      // The placeholder is typically very small (~8KB) compared to real imagery (~50-200KB)
      if (blob.size < 10000) {
        throw new Error(`Street View not available at this location. Try a location on a public road.`);
      }

      results.push({
        blob,
        azimuth: view.azimuth,
      });
    }

    return results;
  }, []);

  /**
   * Handle click on the map to select a location.
   */
  const handleLocationClick = useCallback(async ({ lat, lng }) => {
    setIsLoadingLocation(true);
    setSelectedLocation({ lat, lng, placeName: null, address: null });
    setAppState(APP_STATE.LOCATION_SELECTED);

    try {
      const { placeName, address } = await reverseGeocode(lat, lng);
      setSelectedLocation({ lat, lng, placeName, address });
    } catch (err) {
      console.error('[App] Reverse geocode failed:', err);
      setSelectedLocation({ lat, lng, placeName: 'Unknown Location', address: `${lat.toFixed(4)}, ${lng.toFixed(4)}` });
    } finally {
      setIsLoadingLocation(false);
    }
  }, []);

  /**
   * Handle generate button click from LocationPopup - uses multi-image flow.
   */
  const handleGenerate = useCallback(async () => {
    if (!selectedLocation) return;

    try {
      setAppState(APP_STATE.GENERATING);
      setStatusText('Capturing satellite images...');
      setError(null);

      // Capture 4 satellite images from offset positions
      const images = await captureMultipleViews(selectedLocation.lat, selectedLocation.lng);

      // Generate description for the location
      const textPrompt = generateLocationDescription(
        selectedLocation.placeName,
        selectedLocation.address
      );

      setStatusText('Generating 3D world...');
      const result = await generateWorldMulti(images, textPrompt, (status) => {
        setStatusText(status);
      });

      setViewerUrl(result.viewer_url);
      setAppState(APP_STATE.VIEWING);
      setSelectedLocation(null);
    } catch (err) {
      console.error('Generation failed:', err);
      setError(err.message || 'Generation failed. Please try again.');
      setAppState(APP_STATE.IDLE);
      setSelectedLocation(null);
    }
  }, [selectedLocation, captureMultipleViews]);

  /**
   * Handle closing the location popup.
   */
  const handleCloseLocationPopup = useCallback(() => {
    setAppState(APP_STATE.IDLE);
    setSelectedLocation(null);
    setIsLoadingLocation(false);
  }, []);

  /**
   * Handle closing the world viewer.
   */
  const handleCloseViewer = useCallback(() => {
    setAppState(APP_STATE.IDLE);
    setViewerUrl(null);
  }, []);

  return (
    <div className="relative h-full w-full">
      <MapView ref={mapRef} onLocationClick={handleLocationClick} />

      {appState === APP_STATE.LOCATION_SELECTED && selectedLocation && (
        <LocationPopup
          lat={selectedLocation.lat}
          lng={selectedLocation.lng}
          placeName={selectedLocation.placeName}
          isLoading={isLoadingLocation}
          onGenerate={handleGenerate}
          onClose={handleCloseLocationPopup}
        />
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
