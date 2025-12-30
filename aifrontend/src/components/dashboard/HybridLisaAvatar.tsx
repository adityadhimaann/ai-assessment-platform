import { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api-client";

interface HybridLisaAvatarProps {
  isSpeaking: boolean;
  questionText?: string;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  onAudioReady?: (audioUrl: string) => void;
}

export function HybridLisaAvatar({ 
  isSpeaking, 
  questionText,
  emotion = "neutral",
  size = "xl",
  onAudioReady
}: HybridLisaAvatarProps) {
  const [currentEmotion, setCurrentEmotion] = useState(emotion);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isLoadingVideo, setIsLoadingVideo] = useState(false);
  const [showVideo, setShowVideo] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    setCurrentEmotion(emotion);
  }, [emotion]);

  // Generate D-ID video when speaking starts
  useEffect(() => {
    const generateVideo = async () => {
      if (isSpeaking && questionText) {
        setIsLoadingVideo(true);
        setShowVideo(false);
        
        try {
          console.log("🎬 Starting D-ID video generation...");
          const result = await apiClient.createTalkingAvatar(questionText, emotion);
          
          if (result.status === "ready" && result.video_url) {
            console.log("✅ D-ID video ready:", result.video_url);
            setVideoUrl(result.video_url);
            setShowVideo(true);
            
            // Notify parent that audio is ready (D-ID video includes audio)
            if (onAudioReady) {
              onAudioReady(result.video_url);
            }
          } else {
            console.log("⏳ D-ID video still processing, status:", result.status);
          }
        } catch (error) {
          console.error("❌ Error generating D-ID video:", error);
        } finally {
          setIsLoadingVideo(false);
        }
      } else {
        // Reset when not speaking
        setVideoUrl(null);
        setShowVideo(false);
      }
    };

    generateVideo();
  }, [isSpeaking, questionText, emotion, onAudioReady]);

  // Play video when URL is available
  useEffect(() => {
    if (videoUrl && videoRef.current && showVideo) {
      videoRef.current.play().catch(err => {
        console.error("Error playing video:", err);
      });
    }
  }, [videoUrl, showVideo]);

  // Audio visualization for static avatar
  useEffect(() => {
    if (isSpeaking && !showVideo) {
      // Simulate audio levels for static avatar
      const interval = setInterval(() => {
        setAudioLevel(Math.random() * 0.8 + 0.2);
      }, 100);
      
      return () => clearInterval(interval);
    } else {
      setAudioLevel(0);
    }
  }, [isSpeaking, showVideo]);

  const sizeClasses = {
    sm: "w-32 h-32",
    md: "w-48 h-48",
    lg: "w-64 h-64",
    xl: "w-80 h-80"
  };

  // Professional AI avatar image (Amy from D-ID)
  const getStaticAvatar = () => {
    return "https://create-images-results.d-id.com/DefaultPresenters/Amy/image.png";
  };

  // Calculate mouth opening based on audio level
  const getMouthScale = () => {
    if (!isSpeaking || audioLevel < 0.1) return 1;
    return 1 + (audioLevel * 0.3);
  };

  return (
    <div className="relative flex flex-col items-center">
      {/* Animated background glow */}
      <div className="absolute inset-0 flex items-center justify-center">
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
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 dark:from-blue-900 dark:via-purple-900 dark:to-pink-900" />
          
          {/* Avatar content */}
          <div className="relative w-full h-full flex items-center justify-center">
            {/* Loading overlay */}
            {isLoadingVideo && !showVideo && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm z-20">
                <Loader2 className="w-12 h-12 animate-spin text-primary mb-2" />
                <p className="text-xs text-muted-foreground">Generating video...</p>
              </div>
            )}
            
            {/* D-ID Video (when ready) */}
            {showVideo && videoUrl ? (
              <video
                ref={videoRef}
                src={videoUrl}
                className={cn(
                  "w-full h-full object-cover transition-opacity duration-500",
                  showVideo ? "opacity-100" : "opacity-0"
                )}
                playsInline
                onEnded={() => {
                  setShowVideo(false);
                  setVideoUrl(null);
                }}
              />
            ) : (
              /* Static Avatar (instant fallback) */
              <div className="relative w-full h-full">
                <img 
                  src={getStaticAvatar()}
                  alt="Lisa AI Assistant" 
                  className={cn(
                    "w-full h-full object-cover transition-all duration-300",
                    isSpeaking && "brightness-110"
                  )}
                />
                
                {/* Mouth animation overlay (only when no video) */}
                {isSpeaking && audioLevel > 0.1 && (
                  <div 
                    className="absolute bottom-[35%] left-1/2 -translate-x-1/2 w-12 h-8 rounded-full bg-gradient-to-b from-pink-200/40 to-red-300/40 dark:from-pink-900/40 dark:to-red-900/40 blur-sm transition-transform duration-75"
                    style={{
                      transform: `translateX(-50%) scaleY(${getMouthScale()})`,
                    }}
                  />
                )}
              </div>
            )}
            
            {/* Animated overlay effects */}
            {isSpeaking && (
              <>
                <div className="absolute inset-0 bg-gradient-to-t from-primary/10 via-transparent to-transparent animate-pulse" />
                <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-blue-500/20 to-transparent animate-pulse" />
              </>
            )}
          </div>

          {/* Lip sync indicator dots (only when no video) */}
          {isSpeaking && !showVideo && (
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
            {currentEmotion === "asking" && "🤔"}
            {currentEmotion === "listening" && "👂"}
            {currentEmotion === "thinking" && "💭"}
            {currentEmotion === "happy" && "😊"}
            {currentEmotion === "encouraging" && "👍"}
            {currentEmotion === "neutral" && "😌"}
          </span>
        </div>

        {/* Video status badge */}
        {isLoadingVideo && (
          <div className="absolute -top-3 -left-3 px-2 py-1 rounded-full bg-primary/90 backdrop-blur-sm border border-primary shadow-lg">
            <span className="text-xs font-medium text-primary-foreground flex items-center gap-1">
              <Loader2 className="w-3 h-3 animate-spin" />
              HD
            </span>
          </div>
        )}
        
        {showVideo && (
          <div className="absolute -top-3 -left-3 px-2 py-1 rounded-full bg-green-500/90 backdrop-blur-sm border border-green-500 shadow-lg">
            <span className="text-xs font-medium text-white">
              ✓ HD
            </span>
          </div>
        )}
      </div>

      {/* Audio wave visualization */}
      {isSpeaking && (
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

      {/* Status text */}
      <div className="mt-4 text-center">
        <p className={cn(
          "text-sm font-medium transition-all duration-300",
          isSpeaking 
            ? "text-primary animate-pulse" 
            : "text-muted-foreground"
        )}>
          {isSpeaking && showVideo && "Speaking (HD)..."}
          {isSpeaking && !showVideo && "Speaking..."}
          {!isSpeaking && currentEmotion === "listening" && "Listening..."}
          {!isSpeaking && currentEmotion === "thinking" && "Thinking..."}
          {!isSpeaking && currentEmotion === "neutral" && "Ready"}
        </p>
      </div>
    </div>
  );
}
