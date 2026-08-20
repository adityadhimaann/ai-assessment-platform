import React, { useEffect, useState } from "react";
import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";
import lisaGif from "@/assets/lisa.gif";
import lisaPng from "@/assets/lisa.png";

interface HybridLisaAvatarProps {
  isSpeaking: boolean;
  questionText?: string;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  alignment?: any;
  onAudioReady?: (audioUrl: string) => void;
  className?: string;
}

export function HybridLisaAvatar({ 
  isSpeaking, 
  emotion = "neutral",
  size = "xl",
  className
}: HybridLisaAvatarProps) {
  const [currentEmotion, setCurrentEmotion] = useState(emotion);

  useEffect(() => {
    setCurrentEmotion(emotion);
  }, [emotion]);

  const sizeClasses = {
    sm: "w-32 h-32",
    md: "w-48 h-48",
    lg: "w-64 h-64",
    xl: "w-80 h-80"
  };

  return (
    <div className={cn("relative flex flex-col items-center", className)}>
      {/* Animated background glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {isSpeaking && (
          <>
            <div className="absolute w-full h-full rounded-full bg-gradient-to-r from-primary/20 via-secondary/20 to-primary/20 animate-pulse blur-2xl" />
            <div className="absolute w-[90%] h-[90%] rounded-full bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-pink-500/30 animate-spin-slow blur-xl" />
          </>
        )}
      </div>

      {/* Main avatar container */}
      <div className="relative z-10">
        {/* Outer ring animations */}
        {isSpeaking && (
          <>
            <div className="absolute inset-0 rounded-full border-4 border-primary/40 animate-pulse-ring scale-110" />
            <div className="absolute inset-0 rounded-full border-4 border-secondary/40 animate-pulse-ring animation-delay-300 scale-110" />
            <div className="absolute inset-0 rounded-full border-2 border-blue-500/30 animate-pulse-ring animation-delay-600 scale-110" />
          </>
        )}
        
        {/* Avatar frame */}
        <div className={cn(
          "relative rounded-full overflow-hidden transition-all duration-500 shadow-2xl",
          sizeClasses[size],
          isSpeaking 
            ? "border-8 border-primary/60 shadow-primary/50 scale-105 ring-4 ring-primary/20" 
            : "border-8 border-border/50 shadow-lg scale-100"
        )}>
          {/* Avatar image */}
          <div className="relative w-full h-full flex items-center justify-center bg-slate-900">
            <img 
              src={isSpeaking ? lisaGif : lisaPng}
              alt="Lisa AI Assistant" 
              className={cn(
                "w-full h-full object-cover transition-all duration-300",
                isSpeaking && "brightness-105"
              )}
            />
            {isSpeaking && (
              <div className="absolute inset-0 bg-gradient-to-t from-primary/10 via-transparent to-transparent pointer-events-none" />
            )}
          </div>
        </div>

        {/* Volume indicator badge */}
        <div className={cn(
          "absolute -bottom-3 -right-3 p-3 rounded-full transition-all duration-300 shadow-lg",
          isSpeaking 
            ? "bg-primary text-primary-foreground scale-110 animate-pulse" 
            : "bg-muted text-muted-foreground scale-90 opacity-70"
        )}>
          {isSpeaking ? (
            <Volume2 className="w-5 h-5" />
          ) : (
            <VolumeX className="w-5 h-5" />
          )}
        </div>

        {/* Emotion indicator badge */}
        <div className="absolute -top-3 -right-3 px-3 py-1 rounded-full bg-background/90 backdrop-blur-sm border border-border shadow-lg">
          <span className="text-xs font-medium text-foreground">
            {currentEmotion === "asking" && "🤔 Asking"}
            {currentEmotion === "listening" && "👂 Listening"}
            {currentEmotion === "thinking" && "💭 Thinking"}
            {currentEmotion === "happy" && "😊 Great"}
            {currentEmotion === "encouraging" && "👍 Encouraging"}
            {currentEmotion === "neutral" && "😌 Ready"}
          </span>
        </div>
      </div>

      {/* Audio wave visualization */}
      {isSpeaking && (
        <div className="mt-6 flex items-center gap-1 h-12">
          {[...Array(20)].map((_, i) => {
            const intensity = Math.abs(Math.sin((i / 20) * Math.PI));
            return (
              <div
                key={i}
                className="w-1 bg-gradient-to-t from-primary to-secondary rounded-full animate-pulse"
                style={{
                  height: `${20 + intensity * 80}%`,
                  animationDelay: `${i * 50}ms`,
                  opacity: 0.5 + intensity * 0.5
                }}
              />
            );
          })}
        </div>
      )}

      {/* Status text */}
      <div className="mt-4 text-center">
        <p className={cn(
          "text-sm font-medium transition-all duration-300",
          isSpeaking 
            ? "text-primary animate-pulse" 
            : "text-muted-foreground"
        )}>
          {isSpeaking && "Lisa is speaking..."}
          {!isSpeaking && currentEmotion === "listening" && "Lisa is listening..."}
          {!isSpeaking && currentEmotion === "thinking" && "Thinking..."}
          {!isSpeaking && currentEmotion === "neutral" && "Ready"}
        </p>
      </div>
    </div>
  );
}
