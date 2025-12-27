import { cn } from "@/lib/utils";
import { Mic, MicOff } from "lucide-react";

interface WaveformVisualizerProps {
  isActive: boolean;
  className?: string;
}

export function WaveformVisualizer({ isActive, className }: WaveformVisualizerProps) {
  const bars = 24;
  
  return (
    <div className={cn(
      "glass-card rounded-xl p-6 transition-all duration-500",
      isActive && "glow-accent border-accent/40",
      className
    )}>
      <div className="flex items-center gap-3 mb-4">
        <div className={cn(
          "h-10 w-10 rounded-full flex items-center justify-center transition-all duration-300",
          isActive 
            ? "bg-gradient-to-br from-primary to-secondary animate-pulse-glow" 
            : "bg-muted"
        )}>
          {isActive ? (
            <Mic className="h-5 w-5 text-primary-foreground" />
          ) : (
            <MicOff className="h-5 w-5 text-muted-foreground" />
          )}
        </div>
        <div>
          <p className="text-sm font-medium text-foreground">
            {isActive ? "Listening..." : "Voice Input"}
          </p>
          <p className="text-xs text-muted-foreground">
            {isActive ? "Speak your answer clearly" : "Click to start recording"}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-center gap-1 h-16 bg-background/30 rounded-lg px-4">
        {Array.from({ length: bars }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "w-1 rounded-full transition-all duration-150",
              isActive 
                ? "bg-gradient-to-t from-primary to-secondary" 
                : "bg-muted-foreground/30"
            )}
            style={{
              height: isActive ? `${Math.random() * 100}%` : "20%",
              animationDelay: `${i * 0.05}s`,
              animation: isActive ? `waveform ${0.5 + Math.random() * 0.5}s ease-in-out infinite` : "none",
            }}
          />
        ))}
      </div>
    </div>
  );
}
