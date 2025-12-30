import { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api-client";

interface RealisticLisaAvatarProps {
  isSpeaking: boolean;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  questionText?: string;
  size?: "sm" | "md" | "lg" | "xl";
}

export function RealisticLisaAvatar({ 
  isSpeaking, 
  emotion = "neutral",
  questionText,
  size = "xl" 
}: RealisticLisaAvatarProps) {
  const [currentEmotion, setCurrentEmotion] = useState(emotion);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isLoadingVideo, setIsLoadingVideo] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [useFallback, setUseFallback] = useState(false);

  useEffect(() => {
    setCurrentEmotion(emotion);
  }, [emotion]);

  // Generate avatar video when speaking
  useEffect(() => {
    const generateAvatar = async () => {
      if (isSpeaking && questionText && !useFallback) {
        setIsLoadingVideo(true);
        try {
          const result = await apiClient.createTalkingAvatar(questionText, emotion);
          
          if (result.status === "ready" && result.video_url) {
            setVideoUrl(result.video_url);
          } else if (result.status === "disabled") {
            // D-ID not configured, use fallback
            setUseFallback(true);
          }
        } catch (error) {
          console.error("Error generating avatar:", error);
          setUseFallback(true);
        } finally {
          setIsLoadingVideo(false);
        }
      }
    };

    generateAvatar();
  }, [isSpeaking, questionText, emotion, useFallback]);

  // Play video when URL is available
  useEffect(() => {
    if (videoUrl && videoRef.current) {
      videoRef.current.play().catch(err => {
        console.error("Error playing video:", err);
      });
    }
  }, [videoUrl]);

  const sizeClasses = {
    sm: "w-32 h-32",
    md: "w-48 h-48",
    lg: "w-64 h-64",
    xl: "w-80 h-80"
  };

  // Fallback avatar images (professional AI-generated avatars)
  const getFallbackAvatar = () => {
    // Using professional AI avatar images
    const avatarImages = {
      neutral: "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg",
      asking: "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg",
      listening: "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg",
      thinking: "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg",
      happy: "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg",
      encouraging: "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg"
    };
    
    return avatarImages[currentEmotion];
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
          
          {/* Avatar video/image */}
          <div className="relative w-full h-full flex items-center justify-center">
            {isLoadingVideo && (
              <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-10">
                <Loader2 className="w-12 h-12 animate-spin text-primary" />
              </div>
            )}
            
            {videoUrl && !useFallback ? (
              <video
                ref={videoRef}
                src={videoUrl}
                className={cn(
                  "w-full h-full object-cover transition-all duration-300",
                  isSpeaking && "scale-105"
                )}
                playsInline
                onEnded={() => setVideoUrl(null)}
              />
            ) : (
              <img 
                src={getFallbackAvatar()}
                alt="Lisa AI Assistant" 
                className={cn(
                  "w-full h-full object-cover transition-all duration-300",
                  isSpeaking && "scale-105"
                )}
              />
            )}
            
            {/* Animated overlay effects */}
            {isSpeaking && (
              <>
                <div className="absolute inset-0 bg-gradient-to-t from-primary/10 via-transparent to-transparent animate-pulse" />
                <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-blue-500/20 to-transparent animate-pulse" />
              </>
            )}
          </div>

          {/* Lip sync indicator (visual representation) */}
          {isSpeaking && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1">
              <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
              <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
              <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
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
      </div>

      {/* Audio wave visualization */}
      {isSpeaking && (
        <div className="mt-6 flex items-center gap-1 h-12">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-gradient-to-t from-primary to-secondary rounded-full animate-audio-wave"
              style={{
                animationDelay: `${i * 50}ms`,
                height: "100%"
              }}
            />
          ))}
        </div>
      )}

      {/* Status text with emotion */}
      <div className="mt-4 text-center">
        <p className={cn(
          "text-sm font-medium transition-all duration-300",
          isSpeaking 
            ? "text-primary animate-pulse" 
            : "text-muted-foreground"
        )}>
          {isSpeaking && "Speaking..."}
          {!isSpeaking && currentEmotion === "listening" && "Listening..."}
          {!isSpeaking && currentEmotion === "thinking" && "Thinking..."}
          {!isSpeaking && currentEmotion === "neutral" && "Ready"}
        </p>
      </div>
    </div>
  );
}
