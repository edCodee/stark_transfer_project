// import { motion } from 'framer-motion';
// import { useWebSocket } from '../hooks/useWebSocket';
// import { Scan, Activity } from 'lucide-react';

// export const PCView = () => {
//   // Nos conectamos como "mobile" temporalmente para escuchar el broadcast del backend
//   // (En nuestro backend, el endpoint /ws/mobile escucha lo que emite /ws/pc)
//   const { event } = useWebSocket('mobile');

//   return (
//     <div className="relative w-screen h-screen bg-slate-950 flex flex-col items-center justify-center overflow-hidden">
      
//       {/* Fondo estilo cuadrícula táctica */}
//       <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px] pointer-events-none" />

//       {/* Header UI */}
//       <div className="absolute top-8 left-8 flex items-center gap-3 text-cyan-500">
//         <Activity className="animate-pulse" />
//         <span className="font-mono tracking-widest text-sm font-bold">STARK LABS // EMITTER NODE</span>
//       </div>
      
//       <div className="absolute top-8 right-8 text-slate-500 font-mono text-xs">
//         STATUS: <span className={event === 'IDLE' ? 'text-slate-400' : 'text-cyan-400'}>{event}</span>
//       </div>

//       {/* Contenedor de la Imagen */}
//       <div className="relative">
//         {/* Radar de fondo */}
//         <div className="absolute inset-0 flex items-center justify-center">
//           <Scan className="w-96 h-96 text-cyan-900/30 animate-spin-slow" />
//         </div>

//         {/* La Imagen con Framer Motion */}
//         <motion.div
//           className="relative z-10 w-80 h-[28rem] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl"
//           animate={{
//             scale: event === 'IMAGE_GRABBED' ? 0.9 : 1,
//             x: event === 'IMAGE_THROWN' ? 1200 : 0, // Sale de la pantalla hacia la derecha
//             opacity: event === 'IMAGE_THROWN' ? 0 : 1,
//             rotateY: event === 'IMAGE_GRABBED' ? 10 : 0,
//             boxShadow: event === 'IMAGE_GRABBED' 
//               ? '0px 0px 40px 10px rgba(6, 182, 212, 0.5)' // Resplandor Cyan
//               : '0px 20px 25px -5px rgba(0, 0, 0, 0.5)',
//             borderColor: event === 'IMAGE_GRABBED' ? '#06b6d4' : '#1e293b'
//           }}
//           transition={{ 
//             type: 'spring', 
//             stiffness: 200, 
//             damping: 20,
//             x: { duration: 0.5, ease: "anticipate" } // Aceleración de lanzamiento
//           }}
//         >
//           <img 
//             src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2000&auto=format&fit=crop" 
//             alt="Target"
//             className="w-full h-full object-cover"
//           />
//         </motion.div>
//       </div>
//     </div>
//   );
// };

import { motion } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import { Scan, Activity, Upload } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

export const PCView = () => {
  // Nos conectamos como 'pc' para poder emitir mensajes al resto de la sala
  const { event, sendMessage } = useWebSocket('pc');
  const [image, setImage] = useState(null);
  const fileInputRef = useRef(null);

  // Convertimos la imagen local a Base64 para poder enviarla por red
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // MAGIA: Cuando Python manda IMAGE_THROWN, nosotros adjuntamos la imagen real y la reenviamos
  useEffect(() => {
    if (event === 'IMAGE_THROWN' && image) {
      sendMessage('REAL_IMAGE_TRANSFER', { image_data: image });
    }
  }, [event, image, sendMessage]);

  return (
    <div className="relative w-screen h-screen bg-slate-950 flex flex-col items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px] pointer-events-none" />

      <div className="absolute top-8 left-8 flex items-center gap-3 text-cyan-500">
        <Activity className="animate-pulse" />
        <span className="font-mono tracking-widest text-sm font-bold">STARK LABS // EMITTER</span>
      </div>
      
      <div className="absolute top-8 right-8 flex gap-4 items-center">
        {/* Botón para cargar imagen real */}
        <input type="file" accept="image/*" ref={fileInputRef} onChange={handleImageUpload} className="hidden" />
        <button 
          onClick={() => fileInputRef.current.click()}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg font-mono text-xs border border-slate-700 transition"
        >
          <Upload size={14} /> Cargar Archivo
        </button>
        <div className="text-slate-500 font-mono text-xs">
          STATUS: <span className={event === 'IDLE' ? 'text-slate-400' : 'text-cyan-400'}>{event}</span>
        </div>
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center justify-center">
          <Scan className="w-96 h-96 text-cyan-900/30 animate-spin-slow" />
        </div>

        <motion.div
          className="relative z-10 w-80 h-[28rem] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-900 flex items-center justify-center"
          animate={{
            scale: event === 'IMAGE_GRABBED' ? 0.9 : 1,
            x: event === 'IMAGE_THROWN' ? 1200 : 0,
            opacity: event === 'IMAGE_THROWN' ? 0 : 1,
            rotateY: event === 'IMAGE_GRABBED' ? 10 : 0,
            boxShadow: event === 'IMAGE_GRABBED' 
              ? '0px 0px 40px 10px rgba(6, 182, 212, 0.5)' 
              : '0px 20px 25px -5px rgba(0, 0, 0, 0.5)',
            borderColor: event === 'IMAGE_GRABBED' ? '#06b6d4' : '#1e293b'
          }}
          transition={{ type: 'spring', stiffness: 200, damping: 20, x: { duration: 0.5, ease: "anticipate" } }}
        >
          {image ? (
            <img src={image} alt="Target" className="w-full h-full object-cover" />
          ) : (
            <span className="text-slate-500 font-mono text-xs text-center px-8">Esperando carga de imagen...</span>
          )}
        </motion.div>
      </div>
    </div>
  );
};