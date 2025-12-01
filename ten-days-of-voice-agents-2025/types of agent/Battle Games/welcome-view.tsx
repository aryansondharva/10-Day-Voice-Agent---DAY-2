// frontend/welcome-view.tsx
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { MicrophoneIcon } from '@phosphor-icons/react/dist/ssr';
import { LiveKitRoom } from './livekit-room';

interface WelcomeViewProps {
  onStartCall: (playerName: string) => void;
  onConnected: (token: string, playerName: string) => void;
}

export const WelcomeView = ({ onStartCall, onConnected }: WelcomeViewProps) => {
  const [playerName, setPlayerName] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const handleStart = async () => {
    if (!playerName.trim()) {
      toast.error('Please enter your stage name');
      return;
    }

    setIsConnecting(true);
    toast.loading('Connecting to the stage...', { id: 'connecting' });

    try {
      const response = await fetch('/api/livekit-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ identity: playerName }),
      });

      if (!response.ok) {
        throw new Error('Failed to get token');
      }

      const data = await response.json();
      setToken(data.token);
      onConnected(data.token, playerName);
      toast.success('Connected!', { id: 'connecting' });
    } catch (error) {
      toast.error('Connection failed, please try again.', { id: 'connecting' });
      setIsConnecting(false);
    }
  };

  if (token) {
    return (
      <LiveKitRoom
        token={token}
        playerName={playerName}
        onDisconnected={() => {
          setToken(null);
          setIsConnecting(false);
        }}
      />
    );
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      {/* Existing gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(249,115,22,0.3),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(251,191,36,0.2),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(249,115,22,0.1),transparent_70%)]" />
      </div>

      <div className="absolute top-0 left-0 h-96 w-96 rounded-full bg-orange-500/20 blur-3xl" />
      <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-yellow-500/20 blur-3xl" />

      <div className="relative z-10 flex min-h-screen items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="w-full max-w-md"
        >
          <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
            
            <div className="relative p-8 md:p-10">
              <div className="mb-8 text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                  className="mb-4 flex justify-center"
                >
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-orange-600 to-red-600 shadow-lg">
                    <MicrophoneIcon size={32} weight="fill" className="text-white" />
                  </div>
                </motion.div>
                
                <h1 className="mb-2 text-3xl font-bold text-white md:text-4xl">
                  Improv Battle
                </h1>
                <p className="text-sm text-white/70 md:text-base">
                  AI-powered voice improv game show
                </p>
              </div>

              <div className="mb-6">
                <label
                  htmlFor="player-name"
                  className="mb-2 block text-sm font-medium text-white/90"
                >
                  Stage Name
                </label>
                <input
                  id="player-name"
                  type="text"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !isConnecting) {
                      handleStart();
                    }
                  }}
                  className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/50 backdrop-blur-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/50"
                  placeholder="Enter your stage name"
                  disabled={isConnecting}
                />
              </div>

              <button
                onClick={handleStart}
                disabled={isConnecting}
                className={`w-full rounded-lg py-3 font-medium text-white transition-all ${
                  isConnecting
                    ? 'cursor-not-allowed bg-orange-700/50'
                    : 'bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500'
                }`}
              >
                {isConnecting ? 'Connecting...' : 'Enter the Stage'}
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};