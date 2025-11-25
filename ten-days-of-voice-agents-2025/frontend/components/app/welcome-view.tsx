import { Button } from '@/components/livekit/button';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

function FloatingCoffeeBeans() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
<<<<<<< HEAD
          className="absolute w-2 h-2 rounded-full bg-green-300/70"
=======
          className="absolute w-2 h-2 rounded-full bg-amber-700/30"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
          initial={{
            x: Math.random() * window.innerWidth,
            y: window.innerHeight + 50,
            scale: 0.5 + Math.random() * 1.5,
            opacity: 0.3 + Math.random() * 0.7,
          }}
          animate={{
            y: -100,
            x: `+=${(Math.random() - 0.5) * 200}`,
            rotate: Math.random() * 360,
          }}
          transition={{
            duration: 10 + Math.random() * 20,
            repeat: Infinity,
            ease: 'linear',
            delay: Math.random() * 5,
          }}
        />
      ))}
    </div>
  );
}

function CoffeeCup() {
  return (
    <motion.div 
      className="relative mb-8"
      animate={{
        y: [0, -10, 0],
      }}
      transition={{
        duration: 4,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    >
      {/* Coffee cup */}
<<<<<<< HEAD
      <div className="relative z-10 w-28 h-28 bg-gradient-to-br from-green-50 to-green-100 rounded-b-3xl rounded-t-lg border-4 border-green-200 shadow-lg">
        {/* Coffee liquid */}
        <motion.div 
          className="absolute top-1 left-1 right-1 bottom-2 bg-gradient-to-b from-green-700 to-green-900 rounded-b-2xl rounded-t-md"
=======
      <div className="relative z-10 w-28 h-28 bg-gradient-to-br from-amber-200 to-amber-300 rounded-b-3xl rounded-t-lg border-4 border-amber-800/80 shadow-lg">
        {/* Coffee liquid */}
        <motion.div 
          className="absolute top-1 left-1 right-1 bottom-2 bg-gradient-to-b from-amber-700 to-amber-900 rounded-b-2xl rounded-t-md"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
          animate={{
            scaleX: [1, 1.02, 0.98, 1],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <div className="absolute inset-0 overflow-hidden">
            <motion.div 
<<<<<<< HEAD
              className="absolute inset-0 bg-gradient-to-r from-transparent via-green-200/10 to-transparent"
=======
              className="absolute inset-0 bg-gradient-to-r from-transparent via-amber-200/10 to-transparent"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
              animate={{
                x: ['-100%', '100%'],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
          </div>
        </motion.div>
        
        {/* Cup handle */}
<<<<<<< HEAD
        <div className="absolute -right-4 top-6 w-7 h-10 border-4 border-green-200 rounded-r-full border-l-0 bg-green-100/30"></div>
=======
        <div className="absolute -right-4 top-6 w-7 h-10 border-4 border-amber-800/80 rounded-r-full border-l-0 bg-amber-100/30"></div>
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
        
        {/* Steam animations */}
        {[1, 2, 3].map((i) => (
          <motion.div
            key={i}
            className="absolute -top-8 left-1/2 w-1.5 h-8 bg-white/40 rounded-full"
            style={{
              left: `${25 + i * 25}%`,
              transform: 'translateX(-50%)',
            }}
            animate={{
              y: [-10, -40, -70, -100],
              opacity: [0.3, 0.7, 0.5, 0],
              scale: [1, 1.5, 2, 2.5],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              repeatType: 'loop',
              delay: i * 0.5,
              ease: 'easeOut',
            }}
          />
        ))}
      </div>
      
      {/* Saucer */}
      <motion.div 
<<<<<<< HEAD
        className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-32 h-4 bg-gradient-to-b from-green-300 to-green-400 rounded-full shadow-md"
=======
        className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-32 h-4 bg-gradient-to-b from-amber-100 to-amber-200 rounded-full shadow-md"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
        animate={{
          scale: [1, 1.02, 1],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      ></motion.div>
    </motion.div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div 
      ref={ref} 
<<<<<<< HEAD
      className="relative min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-green-50 to-green-100 overflow-hidden"
=======
      className="relative min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-amber-50 to-amber-100 overflow-hidden"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
    >
      <FloatingCoffeeBeans />
      
      <AnimatePresence>
        <motion.section 
<<<<<<< HEAD
          className="relative z-10 bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 flex flex-col items-center text-center border border-green-100/50"
=======
          className="relative z-10 bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 flex flex-col items-center text-center border border-amber-100/50"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
          initial={{ opacity: 0, y: 20, scale: 0.98 }}
          animate={{ 
            opacity: 1, 
            y: 0, 
            scale: 1,
            boxShadow: [
              '0 25px 50px -12px rgba(0, 0, 0, 0.05)',
<<<<<<< HEAD
              '0 25px 50px -12px rgba(0, 128, 0, 0.15)',
=======
              '0 25px 50px -12px rgba(146, 64, 14, 0.15)',
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
              '0 25px 50px -12px rgba(0, 0, 0, 0.05)',
            ]
          }}
          transition={{ 
            duration: 0.8,
            ease: [0.16, 1, 0.3, 1],
            boxShadow: {
              duration: 4,
              repeat: Infinity,
              repeatType: 'reverse',
              ease: 'easeInOut',
            }
          }}
        >
          <CoffeeCup />
          
          <motion.h1 
<<<<<<< HEAD
            className="text-4xl font-bold bg-gradient-to-r from-green-800 to-green-600 bg-clip-text text-transparent mb-3"
=======
            className="text-4xl font-bold bg-gradient-to-r from-amber-800 to-amber-600 bg-clip-text text-transparent mb-3"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            Welcome to Brew Haven
          </motion.h1>
          
          <motion.p 
<<<<<<< HEAD
            className="text-green-800/90 mb-8 max-w-prose leading-relaxed text-lg"
=======
            className="text-amber-800/90 mb-8 max-w-prose leading-relaxed text-lg"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            Your friendly AI barista is ready to craft your perfect drink.
<<<<<<< HEAD
            <span className="block mt-2 text-green-700/80 text-base">Just press the button below to begin!</span>
=======
            <span className="block mt-2 text-amber-700/80 text-base">Just press the button below to begin!</span>
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
            className="relative"
          >
            <Button 
              variant="primary" 
              size="lg" 
              onClick={onStartCall} 
<<<<<<< HEAD
              className="relative z-10 mt-2 w-72 font-sans bg-gradient-to-r from-green-400 to-green-500 hover:from-green-500 hover:to-green-600 text-white transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-green-500/20 text-lg h-14 rounded-xl"
            >
              <span className="relative z-10">{startButtonText}</span>
              <motion.span
                className="absolute inset-0 bg-gradient-to-r from-green-50 to-transparent rounded-xl opacity-0"
=======
              className="relative z-10 mt-2 w-72 font-sans bg-gradient-to-r from-amber-700 to-amber-600 hover:from-amber-800 hover:to-amber-700 text-amber-50 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-amber-500/20 text-lg h-14 rounded-xl"
            >
              <span className="relative z-10">{startButtonText}</span>
              <motion.span
                className="absolute inset-0 bg-gradient-to-r from-amber-500 to-amber-400 rounded-xl opacity-0"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
                animate={{
                  opacity: isHovered ? 1 : 0,
                }}
                transition={{ duration: 0.3 }}
              />
            </Button>
            {isHovered && (
              <motion.div 
<<<<<<< HEAD
                className="absolute -inset-1 bg-gradient-to-r from-green-200 to-green-300 rounded-xl blur opacity-75 -z-10"
=======
                className="absolute -inset-1 bg-gradient-to-r from-amber-400 to-amber-300 rounded-xl blur opacity-75 -z-10"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 0.7, scale: 1.05 }}
                transition={{ duration: 0.3 }}
              />
            )}
          </motion.div>
        </motion.section>
      </AnimatePresence>

      <motion.div 
        className="fixed bottom-5 left-0 flex w-full items-center justify-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
<<<<<<< HEAD
        <p className="text-green-100/60 max-w-prose pt-1 text-sm leading-5 font-medium text-center text-pretty md:text-base bg-white/70 px-6 py-3 rounded-full backdrop-blur-sm border border-green-100 shadow-sm">
=======
        <p className="text-amber-800/80 max-w-prose pt-1 text-sm leading-5 font-medium text-center text-pretty md:text-base bg-white/70 px-6 py-3 rounded-full backdrop-blur-sm border border-amber-100 shadow-sm">
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
          Need help? Check out the{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
<<<<<<< HEAD
            className="text-green-700 font-semibold hover:underline underline-offset-2"
=======
            className="text-amber-700 font-semibold hover:underline underline-offset-2"
>>>>>>> dbd3176c29c6123b9f99665b77648ee690cb4847
          >
            Voice AI quickstart
          </a>
        </p>
      </motion.div>
      
      <div className="absolute bottom-4 right-4 text-xs text-amber-800/50">
        BUILT WITH LIVEKIT AGENTS
      </div>
    </div>
  );
};
