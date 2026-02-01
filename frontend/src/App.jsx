import { useState, useCallback, useRef } from 'react';
import MapView from './components/MapView';
import LoadingOverlay from './components/LoadingOverlay';
import LocationPopup from './components/LocationPopup';
import DataFactory from './components/DataFactory';
import ProductDescriptor from './components/ProductDescriptor';
import { reverseGeocode, generateLocationDescription } from './services/geocoding';
import { generateWorldMulti } from './services/api';

const APP_STATE = {
  IDLE: 'IDLE',
  LOCATION_SELECTED: 'LOCATION_SELECTED',
  ADDING_PRODUCT: 'ADDING_PRODUCT',
  GENERATING: 'GENERATING',
  DATA_FACTORY: 'DATA_FACTORY',
};

export default function App() {
  const [appState, setAppState] = useState(APP_STATE.IDLE);
  const [generatedWorlds, setGeneratedWorlds] = useState([]);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [toast, setToast] = useState(null);
  const [product, setProduct] = useState(null);
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
    setProduct(null); // Reset product when selecting new location

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
    if (!selectedLocation || appState !== APP_STATE.LOCATION_SELECTED) return;

    try {
      setAppState(APP_STATE.GENERATING);
      setStatusText('Capturing satellite images...');
      setError(null);

      // Capture 4 satellite images from offset positions
      const images = await captureMultipleViews(selectedLocation.lat, selectedLocation.lng);

      // Generate description for the location
      const locationPrompt = generateLocationDescription(
        selectedLocation.placeName,
        selectedLocation.address
      );

      // Use location description as text prompt
      const textPrompt = locationPrompt;
      console.log('[App] Text prompt:', textPrompt);

      // Prepare product options if product image is provided
      const productOptions = product?.image ? {
        image: product.image,
        position: product.position,
        scale: product.scale,
      } : null;

      if (productOptions) {
        setStatusText('Compositing product into scene...');
        console.log('[App] Product will be composited:', productOptions.position, productOptions.scale);
      }

      setStatusText('Generating 3D world...');
      const result = await generateWorldMulti(images, textPrompt, (status) => {
        setStatusText(status);
      }, productOptions);

      setGeneratedWorlds((prev) => [...prev, {
        ...result,
        placeName: selectedLocation.placeName || 'Unknown',
        createdAt: Date.now(),
      }]);
      setAppState(APP_STATE.IDLE);
      setSelectedLocation(null);
      setProduct(null);
      setToast('World generated. Open Data Factory to view.');
      setTimeout(() => setToast(null), 4000);
    } catch (err) {
      console.error('Generation failed:', err);
      setError(err.message || 'Generation failed. Please try again.');
      setAppState(APP_STATE.IDLE);
      setSelectedLocation(null);
      setProduct(null);
    }
  }, [selectedLocation, product, captureMultipleViews, appState]);

  /**
   * Handle closing the location popup.
   */
  const handleCloseLocationPopup = useCallback(() => {
    setAppState(APP_STATE.IDLE);
    setSelectedLocation(null);
    setIsLoadingLocation(false);
    setProduct(null);
  }, []);

  /**
   * Handle opening the product descriptor.
   */
  const handleAddProduct = useCallback(() => {
    setAppState(APP_STATE.ADDING_PRODUCT);
  }, []);

  /**
   * Handle product confirmation from ProductDescriptor.
   */
  const handleProductConfirm = useCallback((productData) => {
    setProduct(productData);
    setAppState(APP_STATE.LOCATION_SELECTED);
  }, []);

  /**
   * Handle canceling product addition.
   */
  const handleProductCancel = useCallback(() => {
    setAppState(APP_STATE.LOCATION_SELECTED);
  }, []);

  /**
   * Handle removing the product.
   */
  const handleRemoveProduct = useCallback(() => {
    setProduct(null);
  }, []);

  const handleOpenFactory = useCallback(() => {
    setAppState(APP_STATE.DATA_FACTORY);
    setSelectedLocation(null);
  }, []);

  const handleCloseFactory = useCallback(() => {
    setAppState(APP_STATE.IDLE);
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
          product={product}
          onGenerate={handleGenerate}
          onClose={handleCloseLocationPopup}
          onAddProduct={handleAddProduct}
          onRemoveProduct={handleRemoveProduct}
        />
      )}

      {appState === APP_STATE.ADDING_PRODUCT && (
        <ProductDescriptor
          onConfirm={handleProductConfirm}
          onCancel={handleProductCancel}
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

      {appState === APP_STATE.IDLE && (
        <button
          onClick={handleOpenFactory}
          className="fixed top-8 left-8 z-50 px-5 py-2.5 bg-black/80 backdrop-blur-md border border-neutral-700 rounded-full text-white text-sm font-medium hover:bg-black hover:border-neutral-500 transition-all cursor-pointer"
        >
          Data Factory
        </button>
      )}

      {appState === APP_STATE.DATA_FACTORY && (
        <DataFactory onClose={handleCloseFactory} worlds={generatedWorlds} />
      )}

      {toast && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[300] px-5 py-3 bg-neutral-900 border border-neutral-700 rounded-full text-white text-sm font-medium shadow-lg">
          {toast}
        </div>
      )}
    </div>
  );
}
