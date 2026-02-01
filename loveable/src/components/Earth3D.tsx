import { useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Points, PointMaterial, Line } from '@react-three/drei';
import * as THREE from 'three';
import { motion } from 'framer-motion';

interface EarthMeshProps {
  isPulsing: boolean;
  mousePosition: { x: number; y: number };
}

function EarthWireframe({ isPulsing, mousePosition }: EarthMeshProps) {
  const meshRef = useRef<THREE.Group>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  // Generate sphere points - denser for better visualization
  const pointsGeometry = useMemo(() => {
    const points: number[] = [];
    const numPoints = 2000;
    
    for (let i = 0; i < numPoints; i++) {
      const phi = Math.acos(-1 + (2 * i) / numPoints);
      const theta = Math.sqrt(numPoints * Math.PI) * phi;
      
      const radius = 2.2;
      const x = radius * Math.cos(theta) * Math.sin(phi);
      const y = radius * Math.sin(theta) * Math.sin(phi);
      const z = radius * Math.cos(phi);
      
      points.push(x, y, z);
    }
    
    return new Float32Array(points);
  }, []);

  // Generate latitude lines
  const latitudeLines = useMemo(() => {
    const lines: [number, number, number][][] = [];
    const numLatitudes = 8;
    const radius = 2.2;
    
    for (let i = 1; i < numLatitudes; i++) {
      const phi = (Math.PI * i) / numLatitudes;
      const r = radius * Math.sin(phi);
      const y = radius * Math.cos(phi);
      
      const points: [number, number, number][] = [];
      for (let j = 0; j <= 80; j++) {
        const theta = (2 * Math.PI * j) / 80;
        points.push([r * Math.cos(theta), y, r * Math.sin(theta)]);
      }
      lines.push(points);
    }
    
    return lines;
  }, []);

  // Generate longitude lines
  const longitudeLines = useMemo(() => {
    const lines: [number, number, number][][] = [];
    const numLongitudes = 12;
    const radius = 2.2;
    
    for (let i = 0; i < numLongitudes; i++) {
      const theta = (2 * Math.PI * i) / numLongitudes;
      const points: [number, number, number][] = [];
      
      for (let j = 0; j <= 80; j++) {
        const phi = (Math.PI * j) / 80;
        points.push([
          radius * Math.sin(phi) * Math.cos(theta),
          radius * Math.cos(phi),
          radius * Math.sin(phi) * Math.sin(theta)
        ]);
      }
      lines.push(points);
    }
    
    return lines;
  }, []);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001;
      
      const targetRotationX = mousePosition.y * 0.15;
      const targetRotationZ = -mousePosition.x * 0.1;
      
      meshRef.current.rotation.x += (targetRotationX - meshRef.current.rotation.x) * 0.03;
      meshRef.current.rotation.z += (targetRotationZ - meshRef.current.rotation.z) * 0.03;
      
      if (isPulsing) {
        const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.02;
        meshRef.current.scale.setScalar(scale);
      } else {
        meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.05);
      }
    }

    if (glowRef.current) {
      const material = glowRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = isPulsing ? 0.08 + Math.sin(state.clock.elapsedTime * 2) * 0.04 : 0.03;
    }
  });

  const lineOpacity = isPulsing ? 0.5 : 0.25;
  const pointOpacity = isPulsing ? 0.7 : 0.4;

  return (
    <group ref={meshRef}>
      {/* Point cloud */}
      <Points positions={pointsGeometry} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color="#f2f2f2"
          size={0.012}
          sizeAttenuation={true}
          depthWrite={false}
          opacity={pointOpacity}
        />
      </Points>
      
      {/* Latitude lines */}
      {latitudeLines.map((points, index) => (
        <Line
          key={`lat-${index}`}
          points={points}
          color="#f2f2f2"
          lineWidth={0.8}
          transparent
          opacity={lineOpacity}
        />
      ))}
      
      {/* Longitude lines */}
      {longitudeLines.map((points, index) => (
        <Line
          key={`lng-${index}`}
          points={points}
          color="#f2f2f2"
          lineWidth={0.6}
          transparent
          opacity={lineOpacity * 0.6}
        />
      ))}
      
      {/* Inner glow */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[2.1, 48, 48]} />
        <meshBasicMaterial 
          color="#ffffff" 
          transparent 
          opacity={0.03}
          side={THREE.BackSide}
        />
      </mesh>

      {/* Outer atmosphere */}
      <mesh>
        <sphereGeometry args={[2.5, 48, 48]} />
        <meshBasicMaterial 
          color="#ffffff" 
          transparent 
          opacity={isPulsing ? 0.02 : 0.008}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
}

interface Earth3DProps {
  isPulsing: boolean;
  mousePosition: { x: number; y: number };
  isZooming: boolean;
}

export default function Earth3D({ isPulsing, mousePosition, isZooming }: Earth3DProps) {
  return (
    <motion.div 
      className="absolute inset-0 z-0"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ 
        opacity: isZooming ? 0 : 1, 
        scale: isZooming ? 30 : 1,
      }}
      transition={{ 
        opacity: { duration: isZooming ? 1.2 : 1.5, delay: isZooming ? 0 : 0.3 },
        scale: { duration: isZooming ? 1.2 : 1.5, ease: [0.16, 1, 0.3, 1] }
      }}
    >
      <Canvas
        camera={{ position: [0, 0, 7], fov: 40 }}
        style={{ background: 'transparent' }}
        gl={{ alpha: true, antialias: true }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.3} />
        <EarthWireframe isPulsing={isPulsing} mousePosition={mousePosition} />
      </Canvas>
    </motion.div>
  );
}
