import React, { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";
import lisaRealNeutral from "@/assets/lisa_real_neutral.jpg";
import lisaRealSpeaking from "@/assets/lisa_real_speaking.jpg";

interface LisaLipSyncAvatarProps {
  isSpeaking: boolean;
  audioElement?: HTMLAudioElement | null;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function LisaLipSyncAvatar({
  isSpeaking,
  audioElement,
  emotion = "neutral",
  size = "xl",
  className,
}: LisaLipSyncAvatarProps) {
  // Real-time animation states
  const [mouthOpen, setMouthOpen] = useState(0); // 0 (closed) to 1 (wide open)
  const [blinkState, setBlinkState] = useState(0); // 0 (open) to 1 (closed)
  const [headTilt, setHeadTilt] = useState(0);
  const [headY, setHeadY] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);

  // References for Web Audio API & animation loop
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceNodeRef = useRef<MediaElementAudioSourceNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastBlinkTimeRef = useRef<number>(Date.now());
  const nextBlinkIntervalRef = useRef<number>(3200);

  // Filter & lerping state for smooth organic speech motion
  const currentMouthOpenRef = useRef(0);
  const currentLevelRef = useRef(0);

  // Connect Web Audio API to audioElement when available
  useEffect(() => {
    if (!audioElement) return;

    try {
      if (!audioContextRef.current) {
        const AudioCtx =
          window.AudioContext ||
          (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        audioContextRef.current = new AudioCtx();
      }

      const audioCtx = audioContextRef.current;
      if (audioCtx.state === "suspended") {
        audioCtx.resume();
      }

      if (!analyserRef.current) {
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.5;
        analyserRef.current = analyser;

        try {
          if (!sourceNodeRef.current) {
            const source = audioCtx.createMediaElementSource(audioElement);
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            sourceNodeRef.current = source;
          }
        } catch {
          // Element might already be connected
        }
      }
    } catch (err) {
      console.warn("Web Audio API connection fallback:", err);
    }
  }, [audioElement]);

  // Main 60FPS animation loop for real-time lip-sync and face dynamics
  useEffect(() => {
    let phase = 0;

    const animate = () => {
      const now = Date.now();
      phase += 0.06;

      let targetOpen = 0;
      let rawLevel = 0;

      // 1. Calculate mouth shape from audio or natural speech cadence
      if (isSpeaking) {
        if (analyserRef.current && audioElement && !audioElement.paused) {
          const bufferLength = analyserRef.current.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);
          analyserRef.current.getByteFrequencyData(dataArray);

          // Vocal energy (bins 2-25: ~80Hz - 1200Hz)
          let vocalSum = 0;
          for (let i = 2; i <= 25; i++) {
            vocalSum += dataArray[i];
          }
          const vocalAvg = vocalSum / 24;

          // Amplitude calculation
          rawLevel = Math.min(1, vocalAvg / 110);
          targetOpen = Math.min(1, Math.max(0, (vocalAvg - 18) / 95) * 1.35);
        } else {
          // Organic speech syllable modulation when no audio node connected
          const s1 = Math.sin(phase * 4.2);
          const s2 = Math.sin(phase * 8.4);
          const wordPulse = Math.max(0, Math.sin(phase * 1.5));
          const openRaw = Math.max(0, s1 * 0.7 + s2 * 0.3 + 0.25) * wordPulse;

          targetOpen = Math.min(1, openRaw * 1.25);
          rawLevel = targetOpen * 0.85;
        }
      } else {
        targetOpen = 0;
        rawLevel = 0;
      }

      // Smooth interpolation (lerp) for organic lip movement
      currentMouthOpenRef.current += (targetOpen - currentMouthOpenRef.current) * 0.42;
      currentLevelRef.current += (rawLevel - currentLevelRef.current) * 0.35;

      setMouthOpen(currentMouthOpenRef.current);
      setAudioLevel(currentLevelRef.current);

      // 2. Natural Blinking Logic (every 3-5 seconds, takes ~150ms)
      if (now - lastBlinkTimeRef.current > nextBlinkIntervalRef.current) {
        const blinkProgress = (now - lastBlinkTimeRef.current - nextBlinkIntervalRef.current) / 150;
        if (blinkProgress >= 1) {
          lastBlinkTimeRef.current = now;
          nextBlinkIntervalRef.current = 2800 + Math.random() * 3200;
          setBlinkState(0);
        } else {
          // Blink curve: 0 -> 1 -> 0
          const b = Math.sin(blinkProgress * Math.PI);
          setBlinkState(b);
        }
      } else {
        setBlinkState(0);
      }

      // 3. Subtle Head Sway & Breathing motion
      if (isSpeaking) {
        setHeadTilt(Math.sin(phase * 0.7) * 1.8);
        setHeadY(Math.sin(phase * 1.2) * 1.5);
      } else if (emotion === "thinking") {
        setHeadTilt(-2.2);
        setHeadY(-1.0);
      } else if (emotion === "listening") {
        setHeadTilt(1.8);
        setHeadY(1.0);
      } else {
        setHeadTilt(Math.sin(phase * 0.3) * 0.6);
        setHeadY(Math.sin(phase * 0.4) * 1.0);
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isSpeaking, audioElement, emotion]);

  // Size classes
  const sizeMap = {
    sm: "w-36 h-36",
    md: "w-52 h-52",
    lg: "w-68 h-68",
    xl: "w-80 h-80",
  };

  return (
    <div className={cn("relative flex flex-col items-center select-none", className)}>
      {/* Animated surrounding speech glow aura */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {isSpeaking && (
          <>
            <div
              className="absolute rounded-full bg-gradient-to-r from-blue-500/20 via-purple-500/25 to-pink-500/20 blur-2xl transition-transform duration-100"
              style={{
                width: "120%",
                height: "120%",
                transform: `scale(${1 + audioLevel * 0.18})`,
              }}
            />
            <div
              className="absolute rounded-full bg-primary/20 blur-xl transition-transform duration-75"
              style={{
                width: "108%",
                height: "108%",
                transform: `scale(${1 + audioLevel * 0.28})`,
              }}
            />
          </>
        )}
      </div>

      {/* Main Avatar Circle Container */}
      <div className="relative z-10">
        {/* Pulsing Concentric Outer Rings when speaking */}
        {isSpeaking && (
          <>
            <div
              className="absolute inset-0 rounded-full border-4 border-primary/50 animate-pulse-ring"
              style={{ transform: `scale(${1.06 + audioLevel * 0.08})` }}
            />
            <div
              className="absolute inset-0 rounded-full border-2 border-secondary/40 animate-pulse-ring animation-delay-300"
              style={{ transform: `scale(${1.14 + audioLevel * 0.12})` }}
            />
          </>
        )}

        {/* Circular Real-Face Window */}
        <div
          className={cn(
            "relative rounded-full overflow-hidden transition-all duration-300 shadow-2xl bg-slate-950",
            sizeMap[size],
            isSpeaking
              ? "border-4 border-primary shadow-primary/40 ring-4 ring-primary/20"
              : "border-4 border-border/70 shadow-xl"
          )}
          style={{
            transform: `rotate(${headTilt}deg) translateY(${headY}px)`,
            transition: "transform 0.15s ease-out, border-color 0.3s ease",
          }}
        >
          {/* Base Layer: Neutral Real Face */}
          <img
            src={lisaRealNeutral}
            alt="Lisa AI Avatar"
            className="absolute inset-0 w-full h-full object-cover object-center"
            style={{
              transform: `scale(${1 + mouthOpen * 0.015})`,
              transition: "transform 0.08s ease-out",
            }}
          />

          {/* Real-time Lip-Sync Speaking Layer: dynamically blended over mouth area */}
          <div
            className="absolute inset-0 pointer-events-none transition-opacity duration-75"
            style={{
              opacity: Math.min(1, mouthOpen * 1.35),
            }}
          >
            <img
              src={lisaRealSpeaking}
              alt="Lisa Speaking"
              className="w-full h-full object-cover object-center"
              style={{
                transform: `scale(${1 + mouthOpen * 0.015}) translateY(${mouthOpen * 0.8}px)`,
                clipPath: "ellipse(28% 18% at 50% 50%)",
                filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.15))",
              }}
            />
          </div>

          {/* Natural Eye Blinking Overlay */}
          {blinkState > 0.08 && (
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                clipPath: "polygon(34% 31%, 66% 31%, 66% 39%, 34% 39%)",
                opacity: blinkState,
              }}
            >
              <div className="w-full h-full bg-[#dcb8aa]/90 backdrop-blur-[1px]" />
            </div>
          )}

          {/* Subtle Dynamic Ambient Lighting on Speech */}
          {isSpeaking && (
            <div
              className="absolute inset-0 bg-gradient-to-t from-primary/15 via-transparent to-transparent pointer-events-none transition-opacity duration-100"
              style={{ opacity: 0.3 + audioLevel * 0.7 }}
            />
          )}
        </div>

        {/* Real-Time Audio / Volume Indicator Badge */}
        <div
          className={cn(
            "absolute -bottom-3 -right-3 p-3 rounded-full transition-all duration-300 shadow-xl",
            isSpeaking
              ? "bg-primary text-primary-foreground scale-110 shadow-primary/50 animate-pulse"
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

      {/* Live Voice Audio Waveform Bars (synchronized with live frequency amplitude) */}
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

      {/* Real-time Status Text */}
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
