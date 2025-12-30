import { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface FastLisaAvatarProps {
  isSpeaking: boolean;
  audioUrl?: string;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
}

export function FastLisaAvatar({ 
  isSpeaking, 
  audioUrl,
  emotion = "neutral",
  size = "xl" 
}: FastLisaAvatarProps) {
  const [currentEmotion, setCurrentEmotion] = useState(emotion);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    setCurrentEmotion(emotion);
  }, [emotion]);

  // Play audio when URL is provided
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play().then(() => {
        setIsPlaying(true);
        startAudioVisualization();
      }).catch(err => {
        console.error("Error playing audio:", err);
      });
    }
  }, [audioUrl]);

  // Audio visualization for lip-sync simulation
  const startAudioVisualization = () => {
    if (!audioRef.current) return;

    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaElementSource(audioRef.current);
    
    source.connect(analyser);
    analyser.connect(audioContext.destination);
    analyser.fftSize = 256;
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    const updateLevel = () => {
      analyser.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(average / 255); // Normalize to 0-1
      
      if (isPlaying) {
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      }
    };

    updateLevel();
  };

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const sizeClasses = {
    sm: "w-32 h-32",
    md: "w-48 h-48",
    lg: "w-64 h-64",
    xl: "w-80 h-80"
  };

  // Professional AI avatar image (Amy from D-ID)
  const getAvatarImage = () => {
    return "https://create-images-results.d-id.com/DefaultPresenters/Amy/image.png";
  };

  // Calculate mouth opening based on audio level
  const getMouthScale = () => {
    if (!isPlaying || audioLevel < 0.1) return 1;
    return 1 + (audioLevel * 0.3); // Scale mouth area by up to 30%
  };

  return (
    <div className="relative flex flex-col items-center">
      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        onEnded={() => {
          setIsPlaying(false);
          setAudioLevel(0);
        }}
        onPause={() => setIsPlaying(false)}
      />

      {/* Animated background glow */}
      <div className="absolute inset-0 flex items-center justify-center">
        {(isSpeaking || isPlaying) && (
          <>
            <div className="absolute w-full h-full rounded-full bg-gradient-to-r from-primary/20 via-secondary/20 to-primary/20 animate-pulse blur-2xl" />
            <div className="absolute w-[90%] h-[90%] rounded-full bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-pink-500/30 animate-spin-slow blur-xl" />
          </>
        )}
      </div>

      {/* Main avatar container */}
      <div className="relative z-10">
        {/* Outer ring animations */}
        {(isSpeaking || isPlaying) && (
          <>
            <div className="absolute inset-0 rounded-full border-4 border-primary/40 animate-pulse-ring scale-110" />
            <div className="absolute inset-0 rounded-full border-4 border-secondary/40 animate-pulse-ring animation-delay-300 scale-110" />
            <div className="absolute inset-0 rounded-full border-2 border-blue-500/30 animate-pulse-ring animation-delay-600 scale-110" />
          </>
        )}
        
        {/* Avatar frame */}
        <div className={cn(
          "relative rounded-full overflow-hidden transition-all duration-300 shadow-2xl",
          sizeClasses[size],
          (isSpeaking || isPlaying)
            ? "border-8 border-primary/60 shadow-primary/50 scale-105 ring-4 ring-primary/20" 
            : "border-8 border-border/50 shadow-lg scale-100"
        )}>
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 dark:from-blue-900 dark:via-purple-900 dark:to-pink-900" />
          
          {/* Avatar image with lip-sync effect */}
          <div className="relative w-full h-full flex items-center justify-center">
            <div className="relative w-full h-full">
              <img 
                src={getAvatarImage()}
                alt="Lisa AI Assistant" 
                className={cn(
                  "w-full h-full object-cover transition-all duration-100",
                  (isSpeaking || isPlaying) && "brightness-110"
                )}
              />
              
              {/* Mouth animation overlay */}
              {(isSpeaking || isPlaying) && audioLevel > 0.1 && (
                <div 
                  className="absolute bottom-[35%] left-1/2 -translate-x-1/2 w-12 h-8 rounded-full bg-gradient-to-b from-pink-200/40 to-red-300/40 dark:from-pink-900/40 dark:to-red-900/40 blur-sm transition-transform duration-75"
                  style={{
                    transform: `translateX(-50%) scaleY(${getMouthScale()})`,
                  }}
                />
              )}
            </div>
            
            {/* Animated overlay effects */}
            {(isSpeaking || isPlaying) && (
              <>
                <div className="absolute inset-0 bg-gradient-to-t from-primary/10 via-transparent to-transparent animate-pulse" />
                <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-blue-500/20 to-transparent animate-pulse" />
              </>
            )}
          </div>

          {/* Lip sync indicator dots */}
          {(isSpeaking || isPlaying) && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1">
              <div 
                className="w-2 h-2 rounded-full bg-primary transition-all duration-100" 
                style={{ 
                  transform: `scale(${1 + audioLevel})`,
                  opacity: 0.5 + audioLevel * 0.5
                }} 
              />
              <div 
                className="w-2 h-2 rounded-full bg-primary transition-all duration-100" 
                style={{ 
                  transform: `scale(${1 + audioLevel * 0.8})`,
                  opacity: 0.5 + audioLevel * 0.5,
                  transitionDelay: "50ms"
                }} 
              />
              <div 
                className="w-2 h-2 rounded-full bg-primary transition-all duration-100" 
                style={{ 
                  transform: `scale(${1 + audioLevel * 0.6})`,
                  opacity: 0.5 + audioLevel * 0.5,
                  transitionDelay: "100ms"
                }} 
              />
            </div>
          )}
        </div>

        {/* Volume indicator badge */}
        <div className={cn(
          "absolute -bottom-3 -right-3 p-3 rounded-full transition-all duration-300 shadow-lg",
          (isSpeaking || isPlaying)
            ? "bg-primary text-primary-foreground scale-110 animate-pulse" 
            : "bg-muted text-muted-foreground scale-90 opacity-70"
        )}>
          {(isSpeaking || isPlaying) ? (
            <Volume2 className="w-5 h-5" />
          ) : (
            <VolumeX className="w-5 h-5" />
          )}
        </div>

        {/* Emotion indicator badge */}
        <div className="absolute -top-3 -right-3 px-3 py-1 rounded-full bg-background/90 backdrop-blur-sm border border-border shadow-lg">
          <span className="text-xs font-medium text-foreground">
            {currentEmotion === "asking" && "🤔"}
            {currentEmotion === "listening" && "👂"}
            {currentEmotion === "thinking" && "💭"}
            {currentEmotion === "happy" && "😊"}
            {currentEmotion === "encouraging" && "👍"}
            {currentEmotion === "neutral" && "😌"}
          </span>
        </div>
      </div>

      {/* Audio wave visualization */}
      {(isSpeaking || isPlaying) && (
        <div className="mt-6 flex items-center gap-1 h-12">
          {[...Array(20)].map((_, i) => {
            const delay = i * 50;
            const intensity = Math.abs(Math.sin((i / 20) * Math.PI)) * audioLevel;
            return (
              <div
                key={i}
                className="w-1 bg-gradient-to-t from-primary to-secondary rounded-full transition-all duration-100"
                style={{
                  height: `${20 + intensity * 80}%`,
                  opacity: 0.3 + intensity * 0.7
                }}
              />
            );
          })}
        </div>
      )}

      {/* Status text with emotion */}
      <div className="mt-4 text-center">
        <p className={cn(
          "text-sm font-medium transition-all duration-300",
          (isSpeaking || isPlaying)
            ? "text-primary animate-pulse" 
            : "text-muted-foreground"
        )}>
          {(isSpeaking || isPlaying) && "Speaking..."}
          {!isSpeaking && !isPlaying && currentEmotion === "listening" && "Listening..."}
          {!isSpeaking && !isPlaying && currentEmotion === "thinking" && "Thinking..."}
          {!isSpeaking && !isPlaying && currentEmotion === "neutral" && "Ready"}
        </p>
      </div>
    </div>
  );
}
