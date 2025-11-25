import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Coffee, Loader2 } from 'lucide-react';
import { Button } from '@/components/livekit/button';

const MOTION_PROPS = {
  variants: {
    hidden: {
      height: 0,
      opacity: 0,
      marginBottom: 0,
    },
    visible: {
      height: 'auto',
      opacity: 1,
      marginBottom: 12,
    },
  },
  initial: 'hidden',
  transition: {
    duration: 0.3,
    ease: [0.16, 1, 0.3, 1], // cubic-bezier equivalent of easeOutExpo
  },
};

interface CoffeeOrder {
  drinkType: string;
  size: string;
  milk: string;
  extras: string[];
  name: string;
}

interface Message {
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
}

interface ChatInputProps {
  chatOpen: boolean;
  isAgentAvailable?: boolean;
  onSend?: (message: string) => void;
}

export function ChatInput({
  chatOpen,
  isAgentAvailable = false,
  onSend = async () => {},
}: ChatInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isSending, setIsSending] = useState(false);
  const [message, setMessage] = useState<string>('');
  const [transcript, setTranscript] = useState<Message[]>([]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!message.trim()) return;

    try {
      setIsSending(true);
      // Add user message to transcript
      const userMessage = {
        text: message,
        sender: 'user' as const,
        timestamp: new Date()
      };
      setTranscript(prev => [...prev, userMessage]);
      
      await onSend(message);
      setMessage('');
      
      // Simulate agent response (you'll want to replace this with actual agent response)
      setTimeout(() => {
        const agentResponse = {
          text: `Thanks for your order: ${message}. How can I help you further?`,
          sender: 'agent' as const,
          timestamp: new Date()
        };
        setTranscript(prev => [...prev, agentResponse]);
      }, 1000);
    } catch (error) {
      console.error(error);
    } finally {
      setIsSending(false);
    }
  };

  const isDisabled = isSending || !isAgentAvailable || message.trim().length === 0;

  useEffect(() => {
    if (chatOpen && isAgentAvailable) return;
    inputRef.current?.focus();
  }, [chatOpen, isAgentAvailable]);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  return (
    <motion.div
      inert={!chatOpen}
      {...MOTION_PROPS}
      animate={chatOpen ? 'visible' : 'hidden'}
      className="w-full flex flex-col bg-amber-50 rounded-lg shadow-sm border border-amber-100"
    >
      {/* Transcript container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-64">
        {transcript.length === 0 ? (
          <div className="text-center text-amber-600 text-sm py-4">
            Start chatting with the coffee bot...
          </div>
        ) : (
          transcript.map((msg, index) => (
            <div 
              key={index} 
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-xs md:max-w-md rounded-lg px-4 py-2 ${
                  msg.sender === 'user' 
                    ? 'bg-amber-600 text-white rounded-br-none' 
                    : 'bg-white text-gray-800 border border-amber-200 rounded-bl-none'
                }`}
              >
                <p className="text-sm">{msg.text}</p>
                <p className="text-xs opacity-70 mt-1">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2 p-2 border-t border-amber-100">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Coffee className="h-4 w-4 text-amber-400" />
          </div>
          <input
            autoFocus
            ref={inputRef}
            type="text"
            value={message}
            disabled={!chatOpen}
            placeholder="What would you like to order?"
            onChange={(e) => setMessage(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-300 focus:border-amber-300 focus:outline-none transition-all duration-200 disabled:opacity-50 disabled:bg-amber-50"
          />
        </div>

        <Button
          type="submit"
          disabled={isDisabled}
          variant={isDisabled ? 'secondary' : 'default'}
          title={isSending ? 'Sending...' : 'Send'}
          className="h-10 px-4 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
        >
          {isSending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Ordering...</span>
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />   {/* FIXED HERE */}
              <span>Order</span>
            </>
          )}
        </Button>
      </form>
    </motion.div>
  );
}
