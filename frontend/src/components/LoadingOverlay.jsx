export default function LoadingOverlay({ statusText, error, onDismissError }) {
  if (error) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm">
        <div className="bg-neutral-900 border border-neutral-700 rounded-2xl p-8 max-w-md text-center">
          <p className="text-white text-lg font-medium mb-2">
            Generation Failed
          </p>
          <p className="text-neutral-400 text-sm mb-6">{error}</p>
          <button
            onClick={onDismissError}
            className="px-6 py-2.5 bg-white text-black rounded-lg font-medium
                       hover:bg-neutral-200 transition-colors cursor-pointer"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative w-16 h-16 mb-8">
        <div className="absolute inset-0 rounded-full border border-neutral-700" />
        <div className="absolute inset-0 rounded-full border border-transparent border-t-white animate-spin" />
      </div>

      <p className="text-white font-medium text-base tracking-wide">
        {statusText}
      </p>
      <p className="text-neutral-600 text-xs mt-2">
        This usually takes 30–45 seconds
      </p>
    </div>
  );
}
