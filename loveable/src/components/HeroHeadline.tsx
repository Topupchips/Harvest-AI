import { motion } from 'framer-motion';

interface HeroHeadlineProps {
  isZooming: boolean;
}

export default function HeroHeadline({ isZooming }: HeroHeadlineProps) {
  return (
    <motion.div 
      className="absolute inset-0 z-10 flex flex-col items-center justify-center pointer-events-none"
      animate={{
        opacity: isZooming ? 0 : 1,
        scale: isZooming ? 0.8 : 1,
      }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* Decorative line above */}
      <motion.div 
        className="w-px h-16 bg-gradient-to-b from-transparent via-foreground/30 to-foreground/60 mb-8"
        initial={{ scaleY: 0, opacity: 0 }}
        animate={{ scaleY: 1, opacity: 1 }}
        transition={{ duration: 1.2, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
      />

      {/* Main headline */}
      <motion.h1 
        className="display-text text-foreground text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl tracking-[0.2em] md:tracking-[0.25em] text-center select-none"
        initial={{ opacity: 0, y: 20, letterSpacing: '0.5em' }}
        animate={{ opacity: 1, y: 0, letterSpacing: '0.25em' }}
        transition={{ duration: 1.5, delay: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        HARVEST
      </motion.h1>

      <motion.h1 
        className="display-text text-foreground/60 text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl tracking-[0.2em] md:tracking-[0.25em] text-center select-none mt-2"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.5, delay: 1, ease: [0.16, 1, 0.3, 1] }}
      >
        REALITY
      </motion.h1>

      {/* Subtitle */}
      <motion.p 
        className="terminal-text text-muted-foreground text-[10px] md:text-xs tracking-[0.3em] mt-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.4 }}
      >
        WORLD MODEL ROBOTICS TRAINING DATA
      </motion.p>

      {/* Decorative line below */}
      <motion.div 
        className="w-px h-16 bg-gradient-to-t from-transparent via-foreground/30 to-foreground/60 mt-8"
        initial={{ scaleY: 0, opacity: 0 }}
        animate={{ scaleY: 1, opacity: 1 }}
        transition={{ duration: 1.2, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
      />
    </motion.div>
  );
}
