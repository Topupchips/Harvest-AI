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
   * Capture multiple satellite images from offset positions around a location.
   * Since Static Maps doesn't support heading for satellite, we offset the center
   * to capture different perspectives for World Labs multi-image generation.
   * @param {number} lat - Center latitude
   * @param {number} lng - Center longitude
   * @returns {Promise<Array<{blob: Blob, azimuth: number}>>}
   */
  const captureMultipleViews = useCallback(async (lat, lng) => {
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

    // Offset distance in degrees (~100 meters at equator)
    const offset = 0.001;

    // Define views: direction name, azimuth, lat offset, lng offset
    const views = [
      { name: 'North', azimuth: 0, latOff: offset, lngOff: 0 },
      { name: 'East', azimuth: 90, latOff: 0, lngOff: offset },
      { name: 'South', azimuth: 180, latOff: -offset, lngOff: 0 },
      { name: 'West', azimuth: 270, latOff: 0, lngOff: -offset },
    ];

    const results = [];

    for (const view of views) {
      const viewLat = lat + view.latOff;
      const viewLng = lng + view.lngOff;

      const staticUrl =
        `https://maps.googleapis.com/maps/api/staticmap?` +
        `center=${viewLat},${viewLng}&zoom=18&size=1024x1024` +
        `&maptype=satellite&key=${apiKey}`;

      console.log(`[Capture] Fetching ${view.name} view (azimuth ${view.azimuth}) at ${viewLat}, ${viewLng}`);
      const response = await fetch(staticUrl);

      if (!response.ok) {
        throw new Error(`Failed to fetch satellite image for ${view.name} view`);
      }

      const blob = await response.blob();
      console.log(`[Capture] Got ${view.name} view, size:`, blob.size);

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
