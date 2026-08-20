import React, { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";
import lisaRealNeutral from "@/assets/lisa_real_neutral.jpg";
import lisaRealSpeaking from "@/assets/lisa_real_speaking.jpg";

interface LisaLipSyncAvatarProps {
  isSpeaking: boolean;
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function LisaLipSyncAvatar({
  isSpeaking,
  audioElement,
  audioBlob,
  emotion = "neutral",
  size = "xl",
  className,
}: LisaLipSyncAvatarProps) {
  // Exact audio-synchronized states
  const [mouthOpen, setMouthOpen] = useState(0); // 0 (closed) to 1 (full open)
  const [audioLevel, setAudioLevel] = useState(0); // 0 to 1 for visualizer bars
  const [isBlinking, setIsBlinking] = useState(false);

  // Audio PCM data references for sample-accurate lip sync
  const audioBufferRef = useRef<AudioBuffer | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const smoothMouthRef = useRef(0);
  const smoothLevelRef = useRef(0);

  // Blinking timer references
  const lastBlinkRef = useRef(Date.now());
  const nextBlinkIntervalRef = useRef(3500);

  // Decode audio blob into raw PCM waveform when new audio arrives
  useEffect(() => {
    let isCancelled = false;

    const decodeAudio = async () => {
      if (!audioBlob) {
        audioBufferRef.current = null;
        return;
      }

      try {
        if (!audioContextRef.current) {
          const AudioCtx =
            window.AudioContext ||
            (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
          audioContextRef.current = new AudioCtx();
        }

        const arrayBuffer = await audioBlob.arrayBuffer();
        if (isCancelled) return;

        const decoded = await audioContextRef.current.decodeAudioData(arrayBuffer.slice(0));
        if (!isCancelled) {
          audioBufferRef.current = decoded;
        }
      } catch (err) {
        console.warn("PCM audio decode error, using real-time playback fallback:", err);
      }
    };

    decodeAudio();

    return () => {
      isCancelled = true;
    };
  }, [audioBlob]);

  // Main 60 FPS audio sample & wording lip-sync loop
  useEffect(() => {
    let fallbackPhase = 0;

    const syncLipMovement = () => {
      let targetMouth = 0;
      let targetLevel = 0;

      if (isSpeaking) {
        const buffer = audioBufferRef.current;
        const audio = audioElement;

        if (buffer && audio && !audio.paused && !audio.ended) {
          // Exact Sample-Accurate RMS Extraction based on audio.currentTime
          const sampleRate = buffer.sampleRate;
          const currentTime = audio.currentTime;
          const currentSample = Math.floor(currentTime * sampleRate);
          const channelData = buffer.getChannelData(0);

          // 20ms analysis window centered on current playback time
          const windowSize = Math.floor(sampleRate * 0.02);
          const start = Math.max(0, currentSample - Math.floor(windowSize / 2));
          const end = Math.min(channelData.length, start + windowSize);

          if (end > start) {
            let sumSq = 0;
            for (let i = start; i < end; i++) {
              const val = channelData[i];
              sumSq += val * val;
            }
            const rms = Math.sqrt(sumSq / (end - start));

            // Map acoustic speech energy (RMS) directly to mouth aperture
            // Typical voice RMS is between 0.015 (quiet/consonant) and 0.22 (loud vowel)
            const rawNormalized = (rms - 0.012) / 0.16;
            targetMouth = Math.min(1, Math.max(0, rawNormalized));
            targetLevel = Math.min(1, Math.max(0, (rms - 0.008) / 0.18));
          }
        } else {
          // Fallback natural speech rhythm when buffer is decoding
          fallbackPhase += 0.12;
          const wave1 = Math.sin(fallbackPhase * 2.8);
          const wave2 = Math.sin(fallbackPhase * 5.6);
          const cadence = Math.max(0, Math.sin(fallbackPhase * 0.9));
          const raw = Math.max(0, wave1 * 0.6 + wave2 * 0.4 + 0.1) * cadence;
          targetMouth = Math.min(1, raw * 1.2);
          targetLevel = targetMouth * 0.8;
        }
      } else {
        targetMouth = 0;
        targetLevel = 0;
      }

      // Fast-attack, smooth-decay filter for natural human lip articulation
      const attackSpeed = targetMouth > smoothMouthRef.current ? 0.75 : 0.45;
      smoothMouthRef.current += (targetMouth - smoothMouthRef.current) * attackSpeed;
      smoothLevelRef.current += (targetLevel - smoothLevelRef.current) * 0.4;

      setMouthOpen(smoothMouthRef.current);
      setAudioLevel(smoothLevelRef.current);

      // Natural eye blinking (subtle, non-distracting)
      const now = Date.now();
      if (now - lastBlinkRef.current > nextBlinkIntervalRef.current) {
        if (now - lastBlinkRef.current > nextBlinkIntervalRef.current + 160) {
          lastBlinkRef.current = now;
          nextBlinkIntervalRef.current = 2800 + Math.random() * 3200;
          setIsBlinking(false);
        } else {
          setIsBlinking(true);
        }
      }

      animationFrameRef.current = requestAnimationFrame(syncLipMovement);
    };

    animationFrameRef.current = requestAnimationFrame(syncLipMovement);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isSpeaking, audioElement]);

  // Size mapping
  const sizeMap = {
    sm: "w-36 h-36",
    md: "w-52 h-52",
    lg: "w-68 h-68",
    xl: "w-80 h-80",
  };

  return (
    <div className={cn("relative flex flex-col items-center select-none", className)}>
      {/* Surrounding speech glow aura */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {isSpeaking && (
          <>
            <div
              className="absolute rounded-full bg-primary/20 blur-2xl transition-opacity duration-150"
              style={{
                width: "115%",
                height: "115%",
                opacity: 0.3 + audioLevel * 0.7,
              }}
            />
            <div
              className="absolute rounded-full bg-blue-500/15 blur-xl transition-opacity duration-150"
              style={{
                width: "105%",
                height: "105%",
                opacity: 0.2 + audioLevel * 0.6,
              }}
            />
          </>
        )}
      </div>

      {/* Main Avatar Container (100% Rock-Solid & Stable - NO ZIGZAG / NO TILT) */}
      <div className="relative z-10">
        {/* Subtle Outer Concentric Ring when speaking */}
        {isSpeaking && (
          <div
            className="absolute inset-0 rounded-full border-2 border-primary/40 animate-pulse-ring"
            style={{ transform: "scale(1.06)" }}
          />
        )}

        {/* Rock-solid, stable circular frame */}
        <div
          className={cn(
            "relative rounded-full overflow-hidden transition-colors duration-300 shadow-2xl bg-slate-950",
            sizeMap[size],
            isSpeaking
              ? "border-4 border-primary shadow-primary/40 ring-4 ring-primary/20"
              : "border-4 border-border/70 shadow-xl"
          )}
        >
          {/* Base Layer: Neutral Photorealistic Face (Completely Stable Anchor) */}
          <img
            src={lisaRealNeutral}
            alt="Lisa AI Avatar"
            className="w-full h-full object-cover object-center"
            draggable={false}
          />

          {/* Real-time Wording-Accurate Lip Layer (Morphed smoothly over the mouth region only) */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              opacity: Math.min(1, mouthOpen * 1.4),
              transition: "opacity 40ms ease-out",
            }}
          >
            <img
              src={lisaRealSpeaking}
              alt="Lisa Speaking Mouth"
              className="w-full h-full object-cover object-center"
              style={{
                clipPath: "ellipse(17% 11% at 50% 50.2%)",
                filter: "drop-shadow(0 2px 3px rgba(0,0,0,0.12))",
              }}
              draggable={false}
            />
          </div>

          {/* Natural Eye Blinking Overlay (Soft and realistic) */}
          {isBlinking && (
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                clipPath: "polygon(34% 31%, 66% 31%, 66% 39%, 34% 39%)",
              }}
            >
              <div className="w-full h-full bg-[#dcb8aa]/90 backdrop-blur-[1px]" />
            </div>
          )}

          {/* Subtle Ambient Speech Glow */}
          {isSpeaking && (
            <div
              className="absolute inset-0 bg-gradient-to-t from-primary/10 via-transparent to-transparent pointer-events-none"
              style={{ opacity: 0.3 + audioLevel * 0.7 }}
            />
          )}
        </div>

        {/* Audio Volume Status Badge */}
        <div
          className={cn(
            "absolute -bottom-3 -right-3 p-3 rounded-full transition-all duration-300 shadow-xl",
            isSpeaking
              ? "bg-primary text-primary-foreground scale-105 shadow-primary/50"
              : "bg-muted text-muted-foreground scale-90 opacity-80"
          )}
        >
          {isSpeaking ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
        </div>

        {/* Emotion Indicator Badge */}
        <div className="absolute -top-3 -right-3 px-3 py-1 rounded-full bg-background/95 backdrop-blur-md border border-border shadow-lg">
          <span className="text-xs font-semibold text-foreground flex items-center gap-1">
            {emotion === "asking" && "🤔 Asking"}
            {emotion === "listening" && "👂 Listening"}
            {emotion === "thinking" && "💭 Thinking"}
            {emotion === "happy" && "😊 Great!"}
            {emotion === "encouraging" && "👍 Encouraging"}
            {emotion === "neutral" && "😌 Ready"}
          </span>
        </div>
      </div>

      {/* Live Voice Audio Waveform Bars (synchronized with live speech volume) */}
      {isSpeaking && (
        <div className="mt-6 flex items-center justify-center gap-1.5 h-10 w-full max-w-[260px]">
          {[...Array(16)].map((_, i) => {
            const phaseShift = Math.sin((i / 16) * Math.PI);
            const dynamicHeight = Math.max(15, phaseShift * audioLevel * 100);
            return (
              <div
                key={i}
                className="w-1.5 bg-gradient-to-t from-primary via-indigo-400 to-pink-400 rounded-full transition-all duration-75"
                style={{
                  height: `${dynamicHeight}%`,
                  opacity: 0.4 + audioLevel * 0.6,
                }}
              />
            );
          })}
        </div>
      )}

      {/* Status Text */}
      <div className="mt-4 text-center">
        <p
          className={cn(
            "text-sm font-semibold tracking-wide transition-all duration-300",
            isSpeaking ? "text-primary animate-pulse" : "text-muted-foreground"
          )}
        >
          {isSpeaking && "Lisa is speaking..."}
          {!isSpeaking && emotion === "listening" && "Lisa is listening to you..."}
          {!isSpeaking && emotion === "thinking" && "Evaluating your response..."}
          {!isSpeaking && emotion === "neutral" && "Ready for your answer"}
        </p>
      </div>
    </div>
  );
}
