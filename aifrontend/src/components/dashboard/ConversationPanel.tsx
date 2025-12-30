import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";

interface Message {
  type: "question" | "answer";
  content: string;
  timestamp?: string;
  isCorrect?: boolean;
}

interface ConversationPanelProps {
  messages: Message[];
  currentTranscript?: string;
  isListening?: boolean;
}

export function ConversationPanel({ 
  messages, 
  currentTranscript,
  isListening 
}: ConversationPanelProps) {
  return (
    <div className="glass-card h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border/50 p-4">
        <h2 className="text-lg font-semibold text-foreground">Conversation</h2>
        <p className="text-sm text-muted-foreground">
          Your interview with Lisa
        </p>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Lisa will start asking questions...</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  "flex gap-3 animate-fade-in-up",
                  message.type === "answer" && "flex-row-reverse"
                )}
              >
                {/* Avatar */}
                <div
                  className={cn(
                    "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
                    message.type === "question"
                      ? "bg-primary/20 text-primary"
                      : "bg-secondary/20 text-secondary"
                  )}
                >
                  {message.type === "question" ? (
                    <Bot className="w-4 h-4" />
                  ) : (
                    <User className="w-4 h-4" />
                  )}
                </div>

                {/* Message bubble */}
                <div
                  className={cn(
                    "flex-1 max-w-[85%] rounded-2xl p-4 shadow-sm",
                    message.type === "question"
                      ? "bg-primary/10 border border-primary/20"
                      : message.isCorrect === true
                      ? "bg-green-500/10 border border-green-500/20"
                      : message.isCorrect === false
                      ? "bg-orange-500/10 border border-orange-500/20"
                      : "bg-secondary/10 border border-secondary/20"
                  )}
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <span className="text-xs font-semibold text-foreground/70">
                      {message.type === "question" ? "Lisa" : "You"}
                    </span>
                    {message.timestamp && (
                      <span className="text-xs text-muted-foreground">
                        {message.timestamp}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </p>
                  {message.isCorrect !== undefined && (
                    <div className="mt-2 pt-2 border-t border-border/30">
                      <span
                        className={cn(
                          "text-xs font-medium",
                          message.isCorrect
                            ? "text-green-600 dark:text-green-400"
                            : "text-orange-600 dark:text-orange-400"
                        )}
                      >
                        {message.isCorrect ? "✓ Correct" : "⚠ Needs Improvement"}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {/* Current transcript (live) */}
          {currentTranscript && (
            <div className="flex gap-3 flex-row-reverse animate-fade-in-up">
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-secondary/20 text-secondary">
                <User className="w-4 h-4" />
              </div>
              <div className="flex-1 max-w-[85%] rounded-2xl p-4 shadow-sm bg-secondary/10 border border-secondary/20 border-dashed">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <span className="text-xs font-semibold text-foreground/70">
                    You {isListening && <span className="text-primary">(speaking...)</span>}
                  </span>
                </div>
                <p className="text-sm text-foreground/70 leading-relaxed whitespace-pre-wrap italic">
                  {currentTranscript}
                </p>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer status */}
      <div className="border-t border-border/50 p-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{messages.filter(m => m.type === "question").length} questions asked</span>
          <span>{messages.filter(m => m.type === "answer").length} answers given</span>
        </div>
      </div>
    </div>
  );
}
