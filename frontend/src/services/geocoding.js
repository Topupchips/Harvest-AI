const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

/**
 * Reverse geocode coordinates to get a human-readable place name.
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @returns {Promise<{ placeName: string, address: string }>}
 */
export async function reverseGeocode(lat, lng) {
  const url = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${GOOGLE_MAPS_API_KEY}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (data.status === 'OK' && data.results.length > 0) {
      const result = data.results[0];

      // Extract meaningful place name from address components
      const components = result.address_components || [];

      // Try to find a good place name (neighborhood, locality, or sublocality)
      const placeName = findPlaceName(components);

      return {
        placeName: placeName || 'Unknown Location',
        address: result.formatted_address || '',
      };
    }

    return {
      placeName: 'Unknown Location',
      address: `${lat.toFixed(4)}, ${lng.toFixed(4)}`,
    };
  } catch (error) {
    console.error('[Geocoding] Error:', error);
    return {
      placeName: 'Unknown Location',
      address: `${lat.toFixed(4)}, ${lng.toFixed(4)}`,
    };
  }
}

/**
 * Find the best place name from address components.
 * Prioritizes: point_of_interest > neighborhood > sublocality > locality > administrative_area
 */
function findPlaceName(components) {
  const priorities = [
    'point_of_interest',
    'establishment',
    'neighborhood',
    'sublocality_level_1',
    'sublocality',
    'locality',
    'administrative_area_level_2',
    'administrative_area_level_1',
  ];

  for (const type of priorities) {
    const component = components.find((c) => c.types.includes(type));
    if (component) {
      return component.long_name;
    }
  }

  return null;
}

/**
 * Generate a description for World Labs based on location info.
 * @param {string} placeName - The place name
 * @param {string} address - The full address
 * @returns {string} - A description suitable for the World Labs text_prompt
 */
export function generateLocationDescription(placeName, address) {
  if (placeName && placeName !== 'Unknown Location') {
    return `Satellite imagery of ${placeName}. ${address}`;
  }
  return `Satellite imagery of location at ${address}`;
}
