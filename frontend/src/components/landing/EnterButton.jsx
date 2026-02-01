import { motion } from 'framer-motion';

export default function EnterButton({
  onHoverStart,
  onHoverEnd,
  onClick,
  isHovered,
  isZooming,
}) {
  return (
    <motion.div
      className="fixed bottom-16 md:bottom-20 left-1/2 z-20"
      initial={{ opacity: 0, y: 30, x: '-50%' }}
      animate={{
        opacity: isZooming ? 0 : 1,
        y: isZooming ? 60 : 0,
        x: '-50%',
      }}
      transition={{
        duration: 1,
        delay: isZooming ? 0 : 1.6,
        ease: [0.16, 1, 0.3, 1],
      }}
    >
      <motion.button
        className="relative group cursor-pointer"
        onHoverStart={onHoverStart}
        onHoverEnd={onHoverEnd}
        onClick={onClick}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Outer glow ring */}
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            background:
              'radial-gradient(circle, hsl(0 0% 95% / 0.1) 0%, transparent 70%)',
          }}
          animate={{
            scale: isHovered ? 1.5 : 1.2,
            opacity: isHovered ? 1 : 0.5,
          }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        />

        {/* Main button container */}
        <div
          className={`
            relative w-36 h-36 md:w-44 md:h-44 rounded-full
            border transition-all duration-700 ease-out
            flex items-center justify-center
            ${
              isHovered
                ? 'bg-[hsl(0_0%_95%)] border-[hsl(0_0%_95%)]'
                : 'bg-transparent border-[hsl(0_0%_95%_/_0.2)]'
            }
          `}
        >
          {/* Animated ring */}
          <motion.div
            className="absolute inset-0 rounded-full border border-[hsl(0_0%_95%_/_0.1)]"
            animate={{
              scale: isHovered ? [1, 1.2] : 1,
              opacity: isHovered ? [0.5, 0] : 0.2,
            }}
            transition={{
              duration: 1.5,
              repeat: isHovered ? Infinity : 0,
              ease: 'easeOut',
            }}
          />

          {/* Button content */}
          <div className="flex flex-col items-center gap-1">
            <span
              className={`
                terminal-text text-[9px] md:text-[10px] tracking-[0.2em] font-medium
                transition-colors duration-500
                ${isHovered ? 'text-[hsl(0_0%_2%)]' : 'text-[hsl(0_0%_95%_/_0.8)]'}
              `}
            >
              ENTER
            </span>
            <div
              className={`w-4 h-px transition-all duration-500 ${
                isHovered
                  ? 'bg-[hsl(0_0%_2%_/_0.5)] w-6'
                  : 'bg-[hsl(0_0%_95%_/_0.3)]'
              }`}
            />
            <span
              className={`
                terminal-text text-[9px] md:text-[10px] tracking-[0.2em] font-medium
                transition-colors duration-500
                ${isHovered ? 'text-[hsl(0_0%_2%)]' : 'text-[hsl(0_0%_95%_/_0.8)]'}
              `}
            >
              FACTORY
            </span>
          </div>

          {/* Corner accents */}
          <svg
            className="absolute inset-0 w-full h-full"
            viewBox="0 0 100 100"
          >
            <motion.circle
              cx="50"
              cy="50"
              r="48"
              fill="none"
              stroke={
                isHovered
                  ? 'hsl(0 0% 2% / 0.3)'
                  : 'hsl(0 0% 95% / 0.1)'
              }
              strokeWidth="0.5"
              strokeDasharray="4 8"
              animate={{ rotate: isHovered ? 360 : 0 }}
              transition={{
                duration: 20,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
          </svg>
        </div>

        {/* Label below */}
        <motion.span
          className="absolute -bottom-8 left-1/2 -translate-x-1/2 terminal-text text-[hsl(0_0%_50%)] text-[8px] tracking-[0.15em] whitespace-nowrap"
          animate={{ opacity: isHovered ? 1 : 0.5 }}
        >
          CLICK TO PROCEED
        </motion.span>
      </motion.button>
    </motion.div>
  );
}
