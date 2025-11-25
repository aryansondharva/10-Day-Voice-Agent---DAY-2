import * as React from 'react';
import { cn } from '@/lib/utils';

// Coffee cup icon for the barista
const CoffeeIcon = ({ className }: { className?: string }) => (
  <svg 
    className={cn('w-4 h-4', className)} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
  >
    <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
    <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
    <line x1="6" y1="1" x2="6" y2="4"></line>
    <line x1="10" y1="1" x2="10" y2="4"></line>
    <line x1="14" y1="1" x2="14" y2="4"></line>
  </svg>
);

// User icon for customer messages
const UserIcon = ({ className }: { className?: string }) => (
  <svg 
    className={cn('w-4 h-4', className)} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
  >
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The locale to use for the timestamp. */
  locale: string;
  /** The timestamp of the message. */
  timestamp: number;
  /** The message to display. */
  message: string;
  /** The origin of the message. */
  messageOrigin: 'local' | 'remote';
  /** The sender's name. */
  name?: string;
  /** Whether the message has been edited. */
  hasBeenEdited?: boolean;
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });
  const isBarista = messageOrigin === 'remote';
  const displayName = isBarista ? 'Barista' : name || 'You';

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn('group flex w-full flex-col gap-1.5 mb-4', className)}
      {...props}
    >
      <div className={cn(
        'flex items-start gap-3',
        isBarista ? 'flex-row' : 'flex-row-reverse'
      )}>
        {/* Icon */}
        <div className={cn(
          'flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0 mt-1',
          isBarista 
            ? 'bg-amber-100 text-amber-800' 
            : 'bg-amber-800 text-amber-50'
        )}>
          {isBarista ? (
            <CoffeeIcon className="w-4 h-4" />
          ) : (
            <UserIcon className="w-4 h-4" />
          )}
        </div>

        {/* Message bubble */}
        <div className={cn(
          'flex-1',
          isBarista ? 'items-start' : 'items-end'
        )}>
          <header className="flex items-center gap-2 mb-1">
            <span className={cn(
              'font-semibold text-sm',
              isBarista ? 'text-amber-900' : 'text-amber-800'
            )}>
              {displayName}
            </span>
            <span className="text-xs text-amber-600 opacity-70">
              {time.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })}
              {hasBeenEdited && '*'}
            </span>
          </header>
          
          <div className={cn(
            'relative px-4 py-2.5 rounded-2xl text-sm max-w-[85%]',
            'shadow-sm',
            isBarista 
              ? 'bg-white border border-amber-100 text-amber-900 rounded-tl-none' 
              : 'bg-amber-800 text-white rounded-tr-none'
          )}>
            {message}
            
            {/* Decorative elements */}
            {isBarista && (
              <div className="absolute -bottom-1 -left-1 w-3 h-3 bg-white border-l border-b border-amber-100 rounded-br-lg"></div>
            )}
            {!isBarista && (
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-amber-800 rounded-bl-lg"></div>
            )}
          </div>
        </div>
      </div>
    </li>
  );
};
