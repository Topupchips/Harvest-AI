import { useState, useRef } from 'react';

const POSITIONS = [
  { label: 'Ground Center', value: 'ground-center' },
  { label: 'Ground Left', value: 'ground-left' },
  { label: 'Ground Right', value: 'ground-right' },
  { label: 'Random on Ground', value: 'ground-random' },
];

const SCALES = [
  { label: 'Small', value: 0.15 },
  { label: 'Medium', value: 0.25 },
  { label: 'Large', value: 0.35 },
];

export default function ProductDescriptor({ onConfirm, onCancel }) {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [position, setPosition] = useState('bottom-center');
  const [scale, setScale] = useState(0.25);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file || !file.type.startsWith('image/')) {
      return;
    }

    setImageFile(file);

    // Create preview URL
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleConfirm = () => {
    if (!imageFile) return;

    onConfirm({
      image: imageFile,
      position,
      scale,
    });
  };

  const handleRemoveImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-dark-900/70 backdrop-blur-sm">
      <div className="bg-dark-800 border border-neon/30 rounded-2xl p-6 max-w-md w-full mx-4 shadow-[0_0_30px_rgba(0,212,255,0.1)] max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-white font-semibold text-lg">Add Product to Scene</h3>
          <button
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-300 transition-colors cursor-pointer p-1"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <p className="text-gray-400 text-sm mb-5">
          Upload a product image. It will be composited into one of the scene views for consistent 3D placement.
        </p>

        {/* Image Upload Zone */}
        {!imagePreview ? (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`
              mb-5 p-8 border-2 border-dashed rounded-xl cursor-pointer
              transition-all duration-200 flex flex-col items-center justify-center
              ${isDragging
                ? 'border-neon bg-neon/10'
                : 'border-gray-600/50 hover:border-neon/50 hover:bg-dark-700/50'
              }
            `}
          >
            <svg
              className={`w-12 h-12 mb-3 ${isDragging ? 'text-neon' : 'text-gray-500'}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className={`text-sm ${isDragging ? 'text-neon' : 'text-gray-400'}`}>
              {isDragging ? 'Drop image here' : 'Drag & drop product image'}
            </p>
            <p className="text-xs text-gray-500 mt-1">or click to browse</p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleInputChange}
              className="hidden"
            />
          </div>
        ) : (
          <div className="mb-5 relative">
            <img
              src={imagePreview}
              alt="Product preview"
              className="w-full h-48 object-contain bg-dark-700 rounded-xl border border-gray-600/50"
            />
            <button
              onClick={handleRemoveImage}
              className="absolute top-2 right-2 p-1.5 bg-dark-800/80 rounded-lg text-gray-400 hover:text-red-400 transition-colors cursor-pointer"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        )}

        {/* Position */}
        <div className="mb-4">
          <label className="block text-gray-300 text-sm font-medium mb-2">Position in Scene</label>
          <select
            value={position}
            onChange={(e) => setPosition(e.target.value)}
            className="w-full bg-dark-700 border border-gray-600/50 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-neon/50"
          >
            {POSITIONS.map((pos) => (
              <option key={pos.value} value={pos.value}>{pos.label}</option>
            ))}
          </select>
        </div>

        {/* Size */}
        <div className="mb-5">
          <label className="block text-gray-300 text-sm font-medium mb-2">Product Size</label>
          <div className="grid grid-cols-3 gap-2">
            {SCALES.map((s) => (
              <button
                key={s.label}
                onClick={() => setScale(s.value)}
                className={`px-3 py-2 rounded-lg text-sm transition-all cursor-pointer ${
                  scale === s.value
                    ? 'bg-neon/20 border border-neon/50 text-neon'
                    : 'bg-dark-700 border border-gray-600/50 text-gray-300 hover:border-gray-500'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2.5 bg-dark-700 border border-gray-600/50 rounded-xl text-gray-300 text-sm font-medium hover:text-white hover:border-gray-400 transition-all cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!imageFile}
            className="flex-1 px-4 py-2.5 bg-neon/10 border border-neon/40 rounded-xl text-neon text-sm font-medium hover:bg-neon/20 hover:border-neon/60 disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            Add Product
          </button>
        </div>
      </div>
    </div>
  );
}
