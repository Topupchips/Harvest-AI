export default function GenerateButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="
        fixed bottom-8 left-1/2 -translate-x-1/2 z-50
        px-8 py-3.5
        bg-dark-800/80 backdrop-blur-md
        border border-neon/40
        rounded-full
        text-neon font-semibold text-base tracking-wide
        shadow-[0_0_20px_rgba(0,212,255,0.15)]
        hover:shadow-[0_0_30px_rgba(0,212,255,0.3)]
        hover:border-neon/70
        hover:bg-dark-700/90
        transition-all duration-300 ease-out
        cursor-pointer
        select-none
        active:scale-95
      "
    >
      <span className="flex items-center gap-2.5">
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
          <circle cx="12" cy="12" r="10" />
          <path d="M2 12h20" />
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
        Generate World
      </span>
    </button>
  );
}
