export default function LocationPopup({
  lat,
  lng,
  placeName,
  isLoading,
  product,
  onGenerate,
  onClose,
  onAddProduct,
  onRemoveProduct,
}) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-neutral-900 border border-neutral-700 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-[0_0_30px_rgba(0,0,0,0.4)]">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/10 border border-neutral-600 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-5 h-5 text-white"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
            </div>
            <div>
              <h3 className="text-white font-semibold text-base">
                {isLoading ? 'Loading location...' : (placeName || 'Selected Location')}
              </h3>
              <p className="text-neutral-500 text-xs mt-0.5">
                {lat.toFixed(6)}, {lng.toFixed(6)}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-neutral-500 hover:text-white transition-colors cursor-pointer p-1"
            aria-label="Close"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-5 h-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <p className="text-neutral-400 text-sm mb-5">
          Generate a 3D world from satellite imagery of this location.
        </p>

        {/* Product Section */}
        {product?.image ? (
          <div className="mb-4 p-3 bg-neutral-800/50 border border-neutral-700/50 rounded-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img
                  src={URL.createObjectURL(product.image)}
                  alt="Product"
                  className="w-10 h-10 rounded-lg object-cover border border-neutral-600"
                />
                <div>
                  <p className="text-white text-sm font-medium">Product Image</p>
                  <p className="text-neutral-400 text-xs">
                    {product.position} · {Math.round(product.scale * 100)}% size
                  </p>
                </div>
              </div>
              <button
                onClick={onRemoveProduct}
                className="text-neutral-500 hover:text-red-400 transition-colors cursor-pointer p-1"
                aria-label="Remove product"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={onAddProduct}
            className="w-full mb-4 px-4 py-3 bg-neutral-800/50 border border-dashed border-neutral-600/50 rounded-xl text-neutral-400 text-sm hover:text-white hover:border-neutral-500 transition-all cursor-pointer flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Add Product to Scene
          </button>
        )}

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="
              flex-1 px-4 py-2.5
              bg-neutral-800 border border-neutral-700
              rounded-xl
              text-neutral-300 text-sm font-medium
              hover:text-white hover:border-neutral-500
              transition-all duration-200
              cursor-pointer
            "
          >
            Cancel
          </button>
          <button
            onClick={onGenerate}
            disabled={isLoading}
            className="
              flex-1 px-4 py-2.5
              bg-white border border-white
              rounded-xl
              text-black text-sm font-medium
              hover:bg-neutral-200
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
              cursor-pointer
              flex items-center justify-center gap-2
            "
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-4 h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M2 12h20" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
            Generate World
          </button>
        </div>
      </div>
    </div>
  );
}
