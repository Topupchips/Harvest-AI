export default function LocationPopup({ lat, lng, placeName, isLoading, onGenerate, onClose }) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-dark-900/60 backdrop-blur-sm">
      <div className="bg-dark-800 border border-neon/30 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-[0_0_30px_rgba(0,212,255,0.1)]">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-neon/10 border border-neon/30 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-5 h-5 text-neon"
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
              <p className="text-gray-400 text-xs mt-0.5">
                {lat.toFixed(6)}, {lng.toFixed(6)}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-300 transition-colors cursor-pointer p-1"
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

        <p className="text-gray-400 text-sm mb-5">
          Generate a 3D world from satellite imagery of this location.
        </p>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="
              flex-1 px-4 py-2.5
              bg-dark-700 border border-gray-600/50
              rounded-xl
              text-gray-300 text-sm font-medium
              hover:text-white hover:border-gray-400
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
              bg-neon/10 border border-neon/40
              rounded-xl
              text-neon text-sm font-medium
              hover:bg-neon/20 hover:border-neon/60
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
