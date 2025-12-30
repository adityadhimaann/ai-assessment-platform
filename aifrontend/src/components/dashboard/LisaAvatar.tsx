import { useEffect, useState } from "react";
import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";
import lisaGif from "@/assets/lisa.gif";
import lisaPng from "@/assets/lisa.png";

interface LisaAvatarProps {
  isSpeaking: boolean;
  message?: string;
  size?: "sm" | "md" | "lg" | "xl";
}

export function LisaAvatar({ isSpeaking, message, size = "lg" }: LisaAvatarProps) {
  const [showMessage, setShowMessage] = useState(false);

  useEffect(() => {
    if (message && isSpeaking) {
      setShowMessage(true);
    } else {
      const timer = setTimeout(() => setShowMessage(false), 500);
      return () => clearTimeout(timer);
    }
  }, [message, isSpeaking]);

  const sizeClasses = {
    sm: "w-16 h-16",
    md: "w-24 h-24",
    lg: "w-40 h-40",
    xl: "w-64 h-64"
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Avatar Container */}
      <div className="relative">
        {/* Animated rings when speaking */}
        {isSpeaking && (
          <>
            <div className="absolute inset-0 rounded-full border-4 border-primary animate-pulse-ring" />
            <div className="absolute inset-0 rounded-full border-4 border-secondary animate-pulse-ring animation-delay-300" />
          </>
        )}
        
        {/* Avatar Image */}
        <div className={cn(
          "relative rounded-full overflow-hidden border-4 transition-all duration-300",
          sizeClasses[size],
          isSpeaking 
            ? "border-primary shadow-lg shadow-primary/50 scale-105" 
            : "border-border shadow-md"
        )}>
          <img 
            src={isSpeaking ? lisaGif : lisaPng}
            alt="Lisa AI Assistant" 
            className="w-full h-full object-cover"
          />
          
          {/* Speaking indicator overlay */}
          {isSpeaking && (
            <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent" />
          )}
        </div>

        {/* Volume indicator */}
        <div className={cn(
          "absolute -bottom-2 -right-2 p-2 rounded-full transition-all duration-300",
          isSpeaking 
            ? "bg-primary text-primary-foreground scale-100" 
            : "bg-muted text-muted-foreground scale-90 opacity-50"
        )}>
          {isSpeaking ? (
            <Volume2 className="w-4 h-4 animate-pulse" />
          ) : (
            <VolumeX className="w-4 h-4" />
          )}
        </div>
      </div>

      {/* Message bubble */}
      {showMessage && message && (
        <div className="relative max-w-md animate-fade-in-up">
          {/* Speech bubble pointer */}
          <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-primary/10 border-l border-t border-primary/20 rotate-45" />
          
          {/* Message content */}
          <div className="glass-card p-4 border border-primary/20 bg-primary/5">
            <p className="text-sm text-foreground/90 text-center leading-relaxed">
              {message}
            </p>
          </div>
        </div>
      )}

      {/* Status text */}
      <div className="text-center">
        <p className={cn(
          "text-sm font-medium transition-all duration-300",
          isSpeaking 
            ? "text-primary animate-pulse" 
            : "text-muted-foreground"
        )}>
          {isSpeaking ? "Lisa is speaking..." : "Lisa"}
        </p>
      </div>
    </div>
  );
}
