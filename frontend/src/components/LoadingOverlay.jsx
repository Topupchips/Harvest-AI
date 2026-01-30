export default function LoadingOverlay({ statusText, error, onDismissError }) {
  if (error) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-dark-900/80 backdrop-blur-sm">
        <div className="bg-dark-800 border border-red-500/40 rounded-2xl p-8 max-w-md text-center">
          <p className="text-red-400 text-lg font-medium mb-2">
            Generation Failed
          </p>
          <p className="text-gray-400 text-sm mb-6">{error}</p>
          <button
            onClick={onDismissError}
            className="px-6 py-2 bg-dark-700 border border-gray-600 rounded-lg text-gray-200
                       hover:border-gray-400 transition-colors cursor-pointer"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-dark-900/80 backdrop-blur-sm">
      <div className="relative w-20 h-20 mb-6">
        <div className="absolute inset-0 rounded-full border-2 border-neon/20" />
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-neon animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 bg-neon rounded-full animate-pulse" />
        </div>
      </div>

      <p className="text-neon font-medium text-lg tracking-wide">
        {statusText}
      </p>
      <p className="text-gray-500 text-sm mt-2">
        This usually takes 30–45 seconds
      </p>
    </div>
  );
}
