import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
}

export const InstructionsPanel = () => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim()) return;
    
    const newMessage: Message = {
      id: Date.now(),
      text: inputValue.trim(),
      sender: 'user',
    };
    
    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col bg-card border border-border/20 rounded-2xl overflow-hidden">
      <div className="px-4 py-3 border-b border-border/20">
        <h2 className="text-primary font-semibold tracking-wide text-sm uppercase">Instructions</h2>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="space-y-3">
              <p className="text-foreground text-lg font-medium opacity-0 animate-fade-in-up">
                <span className="inline-block animate-wave mr-1">👋</span> Hello
              </p>
              <p className="text-foreground opacity-0 animate-[fade-in-up_0.6s_ease-out_0.4s_forwards]">
                how can I help you today?
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] px-3 py-2 rounded-xl text-sm ${
                    message.sender === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-foreground'
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      <div className="p-3 border-t border-border/20">
        <div className="flex items-center gap-2 bg-secondary/50 border border-border/20 rounded-xl px-4 py-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 bg-transparent text-foreground placeholder:text-muted-foreground text-sm outline-none"
          />
          <button 
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="p-1.5 hover:bg-primary/10 rounded-lg transition-smooth disabled:opacity-50"
          >
            <Send className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>
      </div>
    </div>
  );
};
