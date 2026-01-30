import { useEffect } from 'react';

export default function WorldViewer({ url, onClose }) {
  // Open the viewer in a new tab immediately
  useEffect(() => {
    window.open(url, '_blank');
  }, [url]);

  return (
    <div className="fixed inset-0 z-[200] bg-dark-900 flex flex-col items-center justify-center gap-6">
      <div className="w-16 h-16 rounded-full border-2 border-neon/30 flex items-center justify-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="w-8 h-8 text-neon"
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
      </div>

      <div className="text-center">
        <p className="text-neon text-lg font-medium mb-1">World Generated!</p>
        <p className="text-gray-400 text-sm">Opened in a new tab</p>
      </div>

      <div className="flex gap-3 mt-2">
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="
            px-6 py-2.5
            bg-neon/10 border border-neon/40
            rounded-full
            text-neon text-sm font-medium
            hover:bg-neon/20 hover:border-neon/60
            transition-all duration-200
          "
        >
          Open Again
        </a>
        <button
          onClick={onClose}
          className="
            px-6 py-2.5
            bg-dark-800 border border-gray-600/50
            rounded-full
            text-gray-300 text-sm font-medium
            hover:text-white hover:border-gray-400
            transition-all duration-200
            cursor-pointer
          "
        >
          Back to Map
        </button>
      </div>
    </div>
  );
}
