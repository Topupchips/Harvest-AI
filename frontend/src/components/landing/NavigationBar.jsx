import { motion } from 'framer-motion';

export default function NavigationBar({ coordinates }) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-8 py-8 md:px-16 md:py-12">
      <div className="flex justify-between items-start">
        {/* Left Side - Brand */}
        <motion.div
          className="flex flex-col gap-2"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-[hsl(0_0%_95%_/_0.8)]" />
            <span className="display-text text-[hsl(0_0%_95%)] text-sm tracking-[0.25em]">
              HELLO WORLD
            </span>
          </div>
          <span className="terminal-text text-[hsl(0_0%_50%)] text-[10px] ml-5">
            SYS.v1.0
          </span>
        </motion.div>

        {/* Right Side - Coordinates */}
        <motion.div
          className="flex flex-col items-end gap-3"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="flex gap-8">
            <div className="flex flex-col items-end">
              <span className="terminal-text text-[hsl(0_0%_50%)] text-[9px] mb-1">
                LAT
              </span>
              <span className="terminal-text text-[hsl(0_0%_95%_/_0.7)] text-[11px]">
                {coordinates.lat}
              </span>
            </div>
            <div className="flex flex-col items-end">
              <span className="terminal-text text-[hsl(0_0%_50%)] text-[9px] mb-1">
                LNG
              </span>
              <span className="terminal-text text-[hsl(0_0%_95%_/_0.7)] text-[11px]">
                {coordinates.lng}
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </nav>
  );
}
