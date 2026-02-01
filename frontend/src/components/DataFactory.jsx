import { useState, useCallback, useRef, useEffect } from 'react';
import {
  startExtraction,
  getPreviewImageUrl,
  uploadReference,
  startDetection,
  getAnnotatedImageUrl,
  getDownloadUrl,
} from '../services/dataFactory';
import { fetchWorlds } from '../services/api';

const STATE = {
  READY: 'READY',
  RUNNING: 'RUNNING',
  COMPLETE: 'COMPLETE',
  VIEWING_EXISTING: 'VIEWING_EXISTING', // When images already exist in Supabase
  DETECTING: 'DETECTING',
  DETECTION_COMPLETE: 'DETECTION_COMPLETE',
};

function statusText(event) {
  if (!event) return 'Initializing...';
  const { type, data } = event;
  switch (type) {
    case 'extract_start':
      return 'Starting extraction...';
    case 'panorama_found':
      return 'Found panorama URL';
    case 'panorama_downloaded':
      return `Downloaded panorama (${Math.round(data.size_bytes / 1024)}KB)`;
    case 'views_extracted':
      return `Extracted ${data.num_views} perspective views`;
    case 'image_saved':
      return `Saved ${data.filename}`;
    case 'pipeline_complete':
      return `Done! ${data.total_saved} images saved.`;
    case 'detection_start':
      return `Starting GPT Vision detection on ${data.num_images} images...`;
    case 'analyzing':
      return `Analyzing ${data.filename} with GPT Vision...`;
    case 'image_processed':
      return `Processed ${data.filename} (${data.matches} match${data.matches !== 1 ? 'es' : ''})`;
    case 'detection_complete':
      return `Detection complete! ${data.total_matches} total match${data.total_matches !== 1 ? 'es' : ''}.`;
    case 'error':
      return `Error: ${data.message}`;
    default:
      return type;
  }
}

export default function DataFactory({ onClose, worlds: propWorlds }) {
  const [selectedWorld, setSelectedWorld] = useState(null);
  const [state, setState] = useState(STATE.READY);
  const [numViews, setNumViews] = useState(10);
  const [events, setEvents] = useState([]);
  const [savedImages, setSavedImages] = useState([]);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [error, setError] = useState(null);
  const connRef = useRef(null);

  // Detection state
  const [referenceFile, setReferenceFile] = useState(null);
  const [referencePreview, setReferencePreview] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [detectionEvents, setDetectionEvents] = useState([]);
  const [annotatedImages, setAnnotatedImages] = useState([]);
  const [detectionProgress, setDetectionProgress] = useState({ current: 0, total: 0 });
  const [totalMatches, setTotalMatches] = useState(0);
  const detectionConnRef = useRef(null);

  // Supabase worlds state
  const [supabaseWorlds, setSupabaseWorlds] = useState([]);
  const [isLoadingWorlds, setIsLoadingWorlds] = useState(true);

  // Fetch worlds from Supabase on mount
  useEffect(() => {
    async function loadWorlds() {
      try {
        const worlds = await fetchWorlds();
        setSupabaseWorlds(worlds);
      } catch (err) {
        console.error('Failed to fetch worlds from Supabase:', err);
      } finally {
        setIsLoadingWorlds(false);
      }
    }
    loadWorlds();
  }, []);

  // Merge prop worlds with Supabase worlds (avoid duplicates by world_id)
  const worlds = [...(propWorlds || [])];
  supabaseWorlds.forEach((sw) => {
    if (!worlds.some((w) => w.world_id === sw.world_id)) {
      worlds.push({
        ...sw,
        placeName: sw.place_name || sw.text_prompt || 'Supabase World',
      });
    }
  });

  const handleExtract = useCallback((world) => {
    setState(STATE.RUNNING);
    setSelectedWorld(world);
    setEvents([]);
    setSavedImages([]);
    setError(null);
    setProgress({ current: 0, total: numViews });

    connRef.current = startExtraction(world, numViews, {
      onEvent: (type, data) => {
        setEvents((prev) => [...prev, { type, data, ts: Date.now() }]);
        if (type === 'views_extracted') {
          setProgress((prev) => ({ ...prev, total: data.num_views }));
        }
        if (type === 'image_saved') {
          setSavedImages((prev) => [...prev, data]);
          setProgress((prev) => ({ ...prev, current: data.image_index }));
        }
      },
      onComplete: () => setState(STATE.COMPLETE),
      onError: (err) => {
        setError(err.message);
        setState(STATE.COMPLETE);
      },
    });
  }, [numViews]);

  const handleStop = useCallback(() => {
    connRef.current?.close();
    setState(STATE.COMPLETE);
  }, []);

  const handleBack = useCallback(() => {
    connRef.current?.close();
    detectionConnRef.current?.close();
    setState(STATE.READY);
    setSelectedWorld(null);
    setEvents([]);
    setSavedImages([]);
    setProgress({ current: 0, total: 0 });
    setError(null);
    setReferenceFile(null);
    setReferencePreview(null);
    setDetectionEvents([]);
    setAnnotatedImages([]);
    setDetectionProgress({ current: 0, total: 0 });
    setTotalMatches(0);
  }, []);

  // Check if selected world has existing extracted images
  const hasExistingImages = selectedWorld?.extracted_images?.length > 0;
  const existingImages = selectedWorld?.extracted_images || [];

  // Handle selecting a world - auto-show existing images if available
  const handleSelectWorld = useCallback((world) => {
    if (state !== STATE.READY) return;
    setSelectedWorld(world);

    // If world has existing extracted images, show them immediately
    if (world.extracted_images?.length > 0) {
      // Convert existing images to the format used by savedImages
      const images = world.extracted_images.map((img, idx) => ({
        filename: img.filename,
        yaw: img.yaw,
        pitch: img.pitch,
        url: img.url, // Supabase Storage URL
        image_index: idx + 1,
        total_images: world.extracted_images.length,
      }));
      setSavedImages(images);
      setState(STATE.VIEWING_EXISTING);
    }
  }, [state]);

  // Handle re-extraction for worlds that already have images
  const handleReExtract = useCallback(() => {
    if (!selectedWorld) return;
    setState(STATE.READY);
    setSavedImages([]);
  }, [selectedWorld]);

  const handleReferenceSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setReferenceFile(file);
    setReferencePreview(URL.createObjectURL(file));
  }, []);

  const handleRunDetection = useCallback(async () => {
    if (!referenceFile) return;

    try {
      setIsUploading(true);
      setError(null);
      setDetectionEvents([]);
      setAnnotatedImages([]);
      setTotalMatches(0);

      const { reference_id } = await uploadReference(referenceFile);
      setIsUploading(false);

      setState(STATE.DETECTING);
      setDetectionProgress({ current: 0, total: savedImages.length });

      detectionConnRef.current = startDetection(reference_id, {
        onEvent: (type, data) => {
          setDetectionEvents((prev) => [...prev, { type, data, ts: Date.now() }]);
          if (type === 'detection_start') {
            setDetectionProgress((prev) => ({ ...prev, total: data.num_images }));
          }
          if (type === 'image_processed') {
            setAnnotatedImages((prev) => [...prev, data]);
            setDetectionProgress((prev) => ({ ...prev, current: prev.current + 1 }));
            setTotalMatches((prev) => prev + (data.matches || 0));
          }
        },
        onComplete: () => setState(STATE.DETECTION_COMPLETE),
        onError: (err) => {
          setError(err.message);
          setState(STATE.DETECTION_COMPLETE);
        },
      });
    } catch (err) {
      setIsUploading(false);
      setError(err.message || 'Failed to start detection');
    }
  }, [referenceFile, savedImages.length]);

  const handleStopDetection = useCallback(() => {
    detectionConnRef.current?.close();
    setState(STATE.DETECTION_COMPLETE);
  }, []);

  const lastEvent = events[events.length - 1] || null;
  const pct = progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0;
  const lastDetEvent = detectionEvents[detectionEvents.length - 1] || null;
  const detPct = detectionProgress.total > 0 ? Math.round((detectionProgress.current / detectionProgress.total) * 100) : 0;
  const hasWorlds = worlds && worlds.length > 0;

  return (
    <div className="fixed inset-0 z-[200] bg-black flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800">
        <div>
          <h2 className="text-white font-semibold text-lg">Data Factory</h2>
          <p className="text-neutral-500 text-xs">Extract views & detect objects in generated worlds</p>
        </div>
        <button
          onClick={onClose}
          className="text-neutral-500 hover:text-white transition-colors cursor-pointer p-2 text-xl leading-none"
        >
          &times;
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* ---- Sidebar: World List ---- */}
        <div className="w-72 border-r border-neutral-800 flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-800">
            <p className="text-neutral-500 text-xs font-medium uppercase tracking-wider">
              Generated Worlds ({worlds?.length || 0})
            </p>
          </div>

          <div className="flex-1 overflow-y-auto">
            {isLoadingWorlds ? (
              <div className="p-4 text-center">
                <p className="text-neutral-500 text-xs">Loading worlds...</p>
              </div>
            ) : !hasWorlds ? (
              <div className="p-4 text-center">
                <p className="text-neutral-600 text-xs">No worlds yet.</p>
                <p className="text-neutral-700 text-[10px] mt-1">Generate a world from the map first.</p>
              </div>
            ) : (
              worlds.map((world, i) => {
                const isSelected = selectedWorld === world;
                const hasImages = world.extracted_images?.length > 0;
                return (
                  <div
                    key={world.world_id || i}
                    className={`px-4 py-3 border-b border-neutral-900 cursor-pointer transition-colors ${
                      isSelected ? 'bg-white/5 border-l-2 border-l-white' : 'hover:bg-white/5'
                    }`}
                    onClick={() => handleSelectWorld(world)}
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-white text-sm font-medium truncate">
                        {world.placeName || world.place_name || 'World'}
                      </p>
                      {hasImages && (
                        <span className="ml-2 px-1.5 py-0.5 bg-green-900/50 text-green-400 text-[9px] rounded font-medium">
                          {world.extracted_images.length} imgs
                        </span>
                      )}
                    </div>
                    {world.viewer_url && (
                      <a
                        href={world.viewer_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-neutral-400 text-[10px] underline hover:text-white transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Open world &rarr;
                      </a>
                    )}
                  </div>
                );
              })
            )}
          </div>

          {/* Views slider */}
          {hasWorlds && (
            <div className="px-4 py-3 border-t border-neutral-800">
              <label className="block text-neutral-500 text-[10px] uppercase tracking-wider mb-1">
                Views: {numViews}
              </label>
              <input
                type="range"
                min="4"
                max="20"
                value={numViews}
                onChange={(e) => setNumViews(parseInt(e.target.value))}
                className="w-full accent-white"
                disabled={state !== STATE.READY}
              />
            </div>
          )}
        </div>

        {/* ---- Main Content ---- */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* READY — no world selected */}
          {state === STATE.READY && !selectedWorld && (
            <div className="flex items-center justify-center h-full">
              <p className="text-neutral-600 text-sm">
                {hasWorlds ? 'Select a world from the sidebar to extract photos.' : 'Generate a world from the map first.'}
              </p>
            </div>
          )}

          {/* READY — world selected, no existing images */}
          {state === STATE.READY && selectedWorld && (
            <div className="max-w-md mx-auto mt-12 text-center">
              <div className="bg-neutral-900 rounded-xl p-4 border border-neutral-800 mb-6 text-left">
                <p className="text-neutral-500 text-xs mb-1">Selected World</p>
                <p className="text-white text-sm font-medium">{selectedWorld.placeName || selectedWorld.place_name || 'World'}</p>
                {selectedWorld.viewer_url && (
                  <a
                    href={selectedWorld.viewer_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral-400 text-[10px] underline hover:text-white transition-colors mt-1 inline-block"
                  >
                    Open world &rarr;
                  </a>
                )}
              </div>
              <button
                onClick={() => handleExtract(selectedWorld)}
                className="w-full px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-neutral-200 transition-all cursor-pointer"
              >
                Extract {numViews} Photos
              </button>
            </div>
          )}

          {/* VIEWING_EXISTING — world has existing extracted images */}
          {state === STATE.VIEWING_EXISTING && selectedWorld && (
            <>
              <div className="text-center mb-6">
                <p className="text-white text-lg font-medium">{savedImages.length} photos available</p>
                <p className="text-neutral-500 text-sm mt-1">Previously extracted from this world</p>
              </div>
              <ExistingImageGrid images={savedImages} />

              {/* Detection section */}
              {savedImages.length > 0 && (
                <div className="max-w-lg mx-auto mt-10 bg-neutral-900 rounded-xl p-6 border border-neutral-800">
                  <h3 className="text-white text-sm font-semibold mb-1">GPT Vision Object Detection</h3>
                  <p className="text-neutral-500 text-xs mb-4">
                    Upload a reference image of the object you want to find. GPT-4o Vision will locate matching objects in each extracted view.
                  </p>

                  <label className="block mb-4">
                    <span className="text-neutral-500 text-[10px] uppercase tracking-wider">Reference Image</span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleReferenceSelect}
                      className="mt-1 block w-full text-sm text-neutral-400
                        file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0
                        file:text-sm file:font-medium file:bg-white file:text-black
                        file:cursor-pointer hover:file:bg-neutral-200"
                    />
                  </label>

                  {referencePreview && (
                    <div className="mb-4">
                      <img
                        src={referencePreview}
                        alt="Reference"
                        className="w-24 h-24 object-cover rounded-lg border border-neutral-700"
                      />
                    </div>
                  )}

                  <button
                    onClick={handleRunDetection}
                    disabled={!referenceFile || isUploading}
                    className="w-full px-6 py-3 bg-white text-black rounded-xl font-medium
                      hover:bg-neutral-200 transition-all cursor-pointer
                      disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    {isUploading ? 'Uploading reference...' : 'Find Objects with GPT Vision'}
                  </button>
                </div>
              )}

              <div className="flex justify-center gap-4 mt-8">
                <button
                  onClick={handleReExtract}
                  className="px-6 py-2.5 bg-neutral-900 border border-neutral-700 rounded-full text-neutral-300 text-sm font-medium hover:text-white hover:border-neutral-500 transition-all cursor-pointer"
                >
                  Re-extract Photos
                </button>
                <button
                  onClick={handleBack}
                  className="px-6 py-2.5 bg-white text-black rounded-full text-sm font-medium hover:bg-neutral-200 transition-all cursor-pointer"
                >
                  Back to Worlds
                </button>
              </div>
            </>
          )}

          {/* RUNNING — extracting views */}
          {state === STATE.RUNNING && (
            <>
              <div className="max-w-2xl mx-auto mb-8">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-neutral-400 text-sm">{statusText(lastEvent)}</span>
                  <span className="text-white text-sm font-medium">{progress.current}/{progress.total}</span>
                </div>
                <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white rounded-full transition-all duration-500"
                    style={{ width: `${pct}%` }}
                  />
                </div>

                <div className="mt-4 max-h-40 overflow-y-auto bg-neutral-900 rounded-xl p-3 border border-neutral-800">
                  {events.map((e, i) => (
                    <div key={i} className="text-xs text-neutral-500 py-0.5">
                      <span className="text-neutral-600">{new Date(e.ts).toLocaleTimeString()}</span>{' '}
                      <span className={e.type === 'error' ? 'text-red-400' : ''}>{statusText(e)}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleStop}
                  className="mt-4 px-4 py-2 bg-neutral-900 border border-neutral-700 rounded-lg text-neutral-400 text-xs hover:text-white hover:border-neutral-500 transition-colors cursor-pointer"
                >
                  Stop
                </button>
              </div>

              {savedImages.length > 0 && <ImageGrid images={savedImages} />}
            </>
          )}

          {/* COMPLETE — extraction done, show detection form */}
          {state === STATE.COMPLETE && (
            <>
              {error && (
                <div className="bg-neutral-900 border border-red-900 rounded-xl p-4 mb-6 text-red-400 text-sm max-w-2xl mx-auto">
                  {error}
                </div>
              )}
              <div className="text-center mb-6">
                <p className="text-white text-lg font-medium">{savedImages.length} photos extracted</p>
                <p className="text-neutral-500 text-sm mt-1">Saved to data_preview/</p>
              </div>
              <ImageGrid images={savedImages} />

              {/* Detection section */}
              {savedImages.length > 0 && (
                <div className="max-w-lg mx-auto mt-10 bg-neutral-900 rounded-xl p-6 border border-neutral-800">
                  <h3 className="text-white text-sm font-semibold mb-1">GPT Vision Object Detection</h3>
                  <p className="text-neutral-500 text-xs mb-4">
                    Upload a reference image of the object you want to find. GPT-4o Vision will locate matching objects in each extracted view.
                  </p>

                  <label className="block mb-4">
                    <span className="text-neutral-500 text-[10px] uppercase tracking-wider">Reference Image</span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleReferenceSelect}
                      className="mt-1 block w-full text-sm text-neutral-400
                        file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0
                        file:text-sm file:font-medium file:bg-white file:text-black
                        file:cursor-pointer hover:file:bg-neutral-200"
                    />
                  </label>

                  {referencePreview && (
                    <div className="mb-4">
                      <img
                        src={referencePreview}
                        alt="Reference"
                        className="w-24 h-24 object-cover rounded-lg border border-neutral-700"
                      />
                    </div>
                  )}

                  <button
                    onClick={handleRunDetection}
                    disabled={!referenceFile || isUploading}
                    className="w-full px-6 py-3 bg-white text-black rounded-xl font-medium
                      hover:bg-neutral-200 transition-all cursor-pointer
                      disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    {isUploading ? 'Uploading reference...' : 'Find Objects with GPT Vision'}
                  </button>
                </div>
              )}

              <div className="flex justify-center mt-8">
                <button
                  onClick={handleBack}
                  className="px-6 py-2.5 bg-white text-black rounded-full text-sm font-medium hover:bg-neutral-200 transition-all cursor-pointer"
                >
                  Back to Worlds
                </button>
              </div>
            </>
          )}

          {/* DETECTING — running detection pipeline */}
          {state === STATE.DETECTING && (
            <div className="max-w-2xl mx-auto">
              <div className="flex items-center justify-between mb-2">
                <span className="text-neutral-400 text-sm">{statusText(lastDetEvent)}</span>
                <span className="text-white text-sm font-medium">{detectionProgress.current}/{detectionProgress.total}</span>
              </div>
              <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-white rounded-full transition-all duration-500"
                  style={{ width: `${detPct}%` }}
                />
              </div>

              <div className="mt-4 max-h-40 overflow-y-auto bg-neutral-900 rounded-xl p-3 border border-neutral-800">
                {detectionEvents.map((e, i) => (
                  <div key={i} className="text-xs text-neutral-500 py-0.5">
                    <span className="text-neutral-600">{new Date(e.ts).toLocaleTimeString()}</span>{' '}
                    <span className={e.type === 'error' ? 'text-red-400' : ''}>{statusText(e)}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={handleStopDetection}
                className="mt-4 px-4 py-2 bg-neutral-900 border border-neutral-700 rounded-lg text-neutral-400 text-xs hover:text-white hover:border-neutral-500 transition-colors cursor-pointer"
              >
                Stop
              </button>
            </div>
          )}

          {/* DETECTION_COMPLETE — show annotated results */}
          {state === STATE.DETECTION_COMPLETE && (
            <>
              {error && (
                <div className="bg-neutral-900 border border-red-900 rounded-xl p-4 mb-6 text-red-400 text-sm max-w-2xl mx-auto">
                  {error}
                </div>
              )}
              <div className="text-center mb-6">
                <p className="text-white text-lg font-medium">{totalMatches} object{totalMatches !== 1 ? 's' : ''} detected</p>
                <p className="text-neutral-500 text-sm mt-1">
                  across {annotatedImages.length} image{annotatedImages.length !== 1 ? 's' : ''}
                </p>
              </div>

              <AnnotatedImageGrid images={annotatedImages} />

              <div className="flex justify-center gap-4 mt-8">
                <a
                  href={getDownloadUrl()}
                  download
                  className="px-6 py-2.5 bg-white text-black rounded-full text-sm font-medium hover:bg-neutral-200 transition-all inline-block"
                >
                  Download All
                </a>
                <button
                  onClick={handleBack}
                  className="px-6 py-2.5 bg-neutral-900 border border-neutral-700 rounded-full text-neutral-300 text-sm font-medium hover:text-white hover:border-neutral-500 transition-all cursor-pointer"
                >
                  Back to Worlds
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function ImageGrid({ images }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 max-w-6xl mx-auto">
      {images.map((img, i) => (
        <div
          key={i}
          className="relative group bg-neutral-900 rounded-xl overflow-hidden border border-neutral-800 hover:border-neutral-600 transition-colors"
        >
          <img
            src={getPreviewImageUrl(img.filename)}
            alt={`yaw=${img.yaw} pitch=${img.pitch}`}
            className="w-full aspect-square object-cover"
            loading="lazy"
          />
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-neutral-400 text-[10px]">yaw: {img.yaw} | pitch: {img.pitch}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function AnnotatedImageGrid({ images }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 max-w-6xl mx-auto">
      {images.map((img, i) => (
        <div
          key={i}
          className="relative group bg-neutral-900 rounded-xl overflow-hidden border border-neutral-800 hover:border-neutral-600 transition-colors"
        >
          <img
            src={getAnnotatedImageUrl(img.annotated_filename)}
            alt={img.filename}
            className="w-full aspect-square object-cover"
            loading="lazy"
          />
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-neutral-400 text-[10px]">
              {img.matches} match{img.matches !== 1 ? 'es' : ''}
            </p>
          </div>
          {img.matches > 0 && (
            <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-white text-black text-[10px] font-bold flex items-center justify-center">
              {img.matches}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// Grid for existing images loaded from Supabase Storage (uses direct URLs)
function ExistingImageGrid({ images }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 max-w-6xl mx-auto">
      {images.map((img, i) => (
        <div
          key={i}
          className="relative group bg-neutral-900 rounded-xl overflow-hidden border border-neutral-800 hover:border-neutral-600 transition-colors"
        >
          <img
            src={img.url}
            alt={`yaw=${img.yaw} pitch=${img.pitch}`}
            className="w-full aspect-square object-cover"
            loading="lazy"
          />
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-neutral-400 text-[10px]">yaw: {img.yaw} | pitch: {img.pitch}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
