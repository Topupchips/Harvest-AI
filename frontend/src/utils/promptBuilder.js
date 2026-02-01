/**
 * Build an optimized text prompt for World Labs multi-image generation
 * that includes both location context and product placement description.
 */

/**
 * Generate a product description prompt from structured product data.
 * @param {Object} product - Product details
 * @param {string} product.type - Product type (e.g., "Water bottle")
 * @param {string} [product.color] - Product color
 * @param {string} [product.material] - Product material
 * @param {string} [product.size] - Product size (Small, Medium, Large, Extra Large)
 * @param {string} [product.position] - Position description
 * @param {string} [product.additionalDetails] - Additional details
 * @returns {string}
 */
export function buildProductPrompt(product) {
  if (!product || !product.type) {
    return '';
  }

  const parts = [];

  // Build the main description: "A [size] [color] [material] [type]"
  const sizeMap = {
    'Small': 'small',
    'Medium': 'medium-sized',
    'Large': 'large',
    'Extra Large': 'very large',
  };

  const adjectives = [];
  if (product.size && sizeMap[product.size]) {
    adjectives.push(sizeMap[product.size]);
  }
  if (product.color) {
    adjectives.push(product.color.toLowerCase());
  }
  if (product.material) {
    adjectives.push(product.material.toLowerCase());
  }

  const adjectiveStr = adjectives.join(' ');
  parts.push(`A ${adjectiveStr} ${product.type.toLowerCase()}`);

  // Add position
  if (product.position) {
    parts.push(product.position);
  }

  // Add additional details
  if (product.additionalDetails && product.additionalDetails.trim()) {
    parts.push(product.additionalDetails.trim());
  }

  return parts.join('. ') + '.';
}

/**
 * Combine location description and product description into a single prompt.
 * @param {string} locationPrompt - The location description prompt
 * @param {Object|null} product - Product details (or null if no product)
 * @returns {string}
 */
export function buildCombinedPrompt(locationPrompt, product) {
  const productPrompt = buildProductPrompt(product);

  if (!productPrompt) {
    return locationPrompt;
  }

  if (!locationPrompt) {
    return productPrompt;
  }

  // Combine both: location context + product placement
  return `${locationPrompt} ${productPrompt}`;
}
