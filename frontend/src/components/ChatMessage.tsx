import React from 'react';

interface ChatMessageProps {
  sender: string;
  content: string;
  timestamp: string;
  isAI: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ sender, content, timestamp, isAI }) => {
  return (
    <div className={`flex gap-3 ${isAI ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold shrink-0 ${
        isAI 
          ? 'bg-primary/20 text-primary border border-primary/40' 
          : 'bg-secondary text-secondary-foreground border border-border/20'
      }`}>
        {sender[0]}
      </div>
      <div className={`flex-1 ${isAI ? 'text-right' : 'text-left'}`}>
        <div className="flex items-center gap-2 mb-1">
          {isAI ? (
            <>
              <span className="text-xs text-muted-foreground">{timestamp}</span>
              <span className={`text-sm font-medium ${isAI ? 'text-primary' : 'text-foreground'}`}>
                {sender}
              </span>
            </>
          ) : (
            <>
              <span className={`text-sm font-medium ${isAI ? 'text-primary' : 'text-foreground'}`}>
                {sender}
              </span>
              <span className="text-xs text-muted-foreground">{timestamp}</span>
            </>
          )}
        </div>
        <div className={`inline-block px-4 py-3 rounded-xl ${
          isAI 
            ? 'bg-primary/10 border border-primary/30 text-foreground' 
            : 'bg-secondary border border-border/20 text-secondary-foreground'
        }`}>
          <p className="text-sm leading-relaxed">{content}</p>
        </div>
      </div>
    </div>
  );
};
