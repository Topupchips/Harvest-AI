import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Earth3D from './Earth3D';
import NavigationBar from './NavigationBar';
import HeroHeadline from './HeroHeadline';
import EnterButton from './EnterButton';

export default function LandingPage({ onEnter }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isButtonHovered, setIsButtonHovered] = useState(false);
  const [isZooming, setIsZooming] = useState(false);
  const [coordinates, setCoordinates] = useState({
    lat: '--.--.--',
    lng: '--.--.--',
  });

  const handleMouseMove = useCallback((e) => {
    const x = (e.clientX / window.innerWidth) * 2 - 1;
    const y = -(e.clientY / window.innerHeight) * 2 + 1;
    setMousePosition({ x, y });

    const lat = (y * 90).toFixed(2);
    const lng = (x * 180).toFixed(2);
    setCoordinates({
      lat: `${parseFloat(lat) >= 0 ? '+' : ''}${lat}\u00B0`,
      lng: `${parseFloat(lng) >= 0 ? '+' : ''}${lng}\u00B0`,
    });
  }, []);

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [handleMouseMove]);

  const handleEnterClick = () => {
    setIsZooming(true);
    setTimeout(() => {
      onEnter();
    }, 1200);
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[hsl(0_0%_2%)] landing-grid-overlay">
      {/* Ambient mesh gradient */}
      <div className="fixed inset-0 landing-mesh-gradient pointer-events-none" />

      {/* Vignette overlay */}
      <div className="fixed inset-0 pointer-events-none z-40 bg-[radial-gradient(ellipse_at_center,transparent_0%,transparent_50%,hsl(0_0%_2%)_100%)]" />

      {/* Navigation */}
      <NavigationBar coordinates={coordinates} />

      {/* 3D Earth */}
      <Earth3D
        isPulsing={isButtonHovered}
        mousePosition={mousePosition}
        isZooming={isZooming}
      />

      {/* Hero Headline */}
      <HeroHeadline isZooming={isZooming} />

      {/* Enter Button */}
      <EnterButton
        onHoverStart={() => setIsButtonHovered(true)}
        onHoverEnd={() => setIsButtonHovered(false)}
        onClick={handleEnterClick}
        isHovered={isButtonHovered}
        isZooming={isZooming}
      />

      {/* Bottom status bar */}
      <motion.div
        className="fixed bottom-8 left-8 z-30 flex items-center gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: isZooming ? 0 : 1 }}
        transition={{ duration: 1, delay: 2 }}
      >
        <div className="flex items-center gap-2">
          <motion.div
            className="w-1.5 h-1.5 rounded-full bg-[hsl(0_0%_95%_/_0.6)]"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          <span className="terminal-text text-[hsl(0_0%_50%)] text-[9px] tracking-[0.1em]">
            ONLINE
          </span>
        </div>
      </motion.div>

      <motion.div
        className="fixed bottom-8 right-8 z-30"
        initial={{ opacity: 0 }}
        animate={{ opacity: isZooming ? 0 : 1 }}
        transition={{ duration: 1, delay: 2.2 }}
      >
        <span className="terminal-text text-[hsl(0_0%_50%)] text-[9px] tracking-[0.1em]">
          &copy; 2026 AETHER
        </span>
      </motion.div>

      {/* Hyper-zoom transition */}
      <AnimatePresence>
        {isZooming && (
          <motion.div
            className="fixed inset-0 z-50 bg-[hsl(0_0%_95%)]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
