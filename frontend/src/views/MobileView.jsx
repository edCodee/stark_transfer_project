// import { motion, AnimatePresence } from 'framer-motion';
// import { useWebSocket } from '../hooks/useWebSocket';
// import { Smartphone } from 'lucide-react';

// export const MobileView = () => {
//   const { event } = useWebSocket('mobile');
  
//   // Determinamos si el teléfono tiene la imagen
//   const hasImage = event === 'IMAGE_THROWN';

//   return (
//     <div className="w-screen h-screen bg-black flex items-center justify-center overflow-hidden">
      
//       {/* UI de Espera (desaparece cuando llega la imagen) */}
//       <AnimatePresence>
//         {!hasImage && (
//           <motion.div 
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             exit={{ opacity: 0, scale: 0.8 }}
//             className="flex flex-col items-center gap-4 text-slate-600"
//           >
//             <Smartphone className="w-12 h-12 animate-bounce" />
//             <span className="font-mono text-xs tracking-widest uppercase">Waiting for transfer...</span>
//           </motion.div>
//         )}
//       </AnimatePresence>

//       {/* Imagen Recibida */}
//       <AnimatePresence>
//         {hasImage && (
//           <motion.div
//             initial={{ y: 800, scale: 0.8, opacity: 0 }} // Empieza abajo de la pantalla
//             animate={{ y: 0, scale: 1, opacity: 1 }}     // Llega al centro
//             exit={{ y: 800, opacity: 0 }}
//             transition={{ 
//               type: 'spring', 
//               stiffness: 150, 
//               damping: 15 
//             }}
//             className="w-[90%] h-[80%] rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.3)] border border-cyan-900/50"
//           >
//             <img 
//               src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2000&auto=format&fit=crop" 
//               alt="Received"
//               className="w-full h-full object-cover"
//             />
//           </motion.div>
//         )}
//       </AnimatePresence>
//     </div>
//   );
// };

// import { motion, AnimatePresence } from 'framer-motion';
// import { useWebSocket } from '../hooks/useWebSocket';
// import { Smartphone, Download } from 'lucide-react';
// import { useState, useEffect } from 'react';

// export const MobileView = () => {
//   const { event, payload } = useWebSocket('mobile');
//   const [receivedImage, setReceivedImage] = useState(null);

//   // Si nos llega la imagen real, la guardamos en el estado local
//   useEffect(() => {
//     if (event === 'REAL_IMAGE_TRANSFER' && payload?.image_data) {
//       setReceivedImage(payload.image_data);
//     }
//   }, [event, payload]);

//   return (
//     <div className="w-screen h-screen bg-black flex flex-col items-center justify-center overflow-hidden relative">
      
//       <AnimatePresence>
//         {!receivedImage && (
//           <motion.div 
//             initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 0.8 }}
//             className="flex flex-col items-center gap-4 text-slate-600"
//           >
//             <Smartphone className="w-12 h-12 animate-bounce" />
//             <span className="font-mono text-xs tracking-widest uppercase">Waiting for file...</span>
//           </motion.div>
//         )}
//       </AnimatePresence>

//       <AnimatePresence>
//         {receivedImage && (
//           <motion.div
//             initial={{ y: 800, scale: 0.8, opacity: 0 }}
//             animate={{ y: 0, scale: 1, opacity: 1 }}
//             className="w-[90%] h-[75%] rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.3)] border border-cyan-900/50"
//           >
//             <img src={receivedImage} alt="Received" className="w-full h-full object-cover" />
//           </motion.div>
//         )}
//       </AnimatePresence>

//       {/* Botón de Descarga que aparece tras recibir la imagen */}
//       {receivedImage && (
//         <motion.div 
//           initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
//           className="absolute bottom-10"
//         >
//           {/* El tag <a> con el atributo "download" obliga al navegador a descargar el archivo */}
//           <a 
//             href={receivedImage} 
//             download="stark_transfer_recibida.png"
//             className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white px-6 py-3 rounded-full font-bold uppercase tracking-wider text-sm shadow-[0_0_20px_rgba(6,182,212,0.5)] active:scale-95 transition-all"
//           >
//             <Download size={18} /> Guardar Imagen
//           </a>
//         </motion.div>
//       )}
//     </div>
//   );
// };

import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import { Smartphone, Download } from 'lucide-react';
import { useState, useEffect } from 'react';

export const MobileView = () => {
  const { event, payload } = useWebSocket('mobile');
  const [receivedImage, setReceivedImage] = useState(null);

  // 1. MAGIA DE ESTADO: Limpiamos la imagen cuando la PC la "agarra" de regreso
  useEffect(() => {
    if (event === 'REAL_IMAGE_TRANSFER' && payload?.image_data) {
      setReceivedImage(payload.image_data);
    } else if (event === 'IMAGE_GRABBED') {
      // La PC volvió a tomar el control, limpiamos la pantalla del móvil
      setReceivedImage(null);
    }
  }, [event, payload]);

  return (
    // 2. MAGIA CSS: min-h-screen y padding vertical (py-10) permiten el scroll nativo
    <div className="w-full min-h-screen bg-black flex flex-col items-center justify-center py-10 relative">
      
      <AnimatePresence>
        {!receivedImage && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex flex-col items-center gap-4 text-slate-600 absolute top-1/2 -translate-y-1/2"
          >
            <Smartphone className="w-12 h-12 animate-bounce" />
            <span className="font-mono text-xs tracking-widest uppercase">Waiting for file...</span>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {receivedImage && (
          <motion.div
            initial={{ y: 800, scale: 0.8, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            exit={{ y: 800, opacity: 0 }} // Le damos animación de salida al limpiarse
            className="w-[90%] h-[65vh] rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.3)] border border-cyan-900/50 flex-shrink-0"
          >
            <img src={receivedImage} alt="Received" className="w-full h-full object-cover" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3. Reubicamos el botón para que fluya naturalmente debajo de la imagen */}
      <AnimatePresence>
        {receivedImage && (
          <motion.div 
            initial={{ opacity: 0, y: 50 }} 
            animate={{ opacity: 1, y: 0 }} 
            exit={{ opacity: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-8 mb-4"
          >
            <a 
              href={receivedImage} 
              download="stark_transfer_recibida.png"
              className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white px-6 py-3 rounded-full font-bold uppercase tracking-wider text-sm shadow-[0_0_20px_rgba(6,182,212,0.5)] active:scale-95 transition-all"
            >
              <Download size={18} /> Guardar Imagen
            </a>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};