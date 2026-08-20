import React, { useEffect, useRef, useState } from "react";
import { Volume2, VolumeX, Sparkles, Mic, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface ElevenLabsAvatarProps {
  isSpeaking: boolean;
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function ElevenLabsAvatar({
  isSpeaking,
  audioElement,
  audioBlob,
  emotion = "neutral",
  size = "xl",
  className,
}: ElevenLabsAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioBufferRef = useRef<AudioBuffer | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const [audioLevel, setAudioLevel] = useState(0);
  const smoothLevelRef = useRef(0);

  // Decode audio blob into raw PCM for real-time waveform reactions
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

  // 60 FPS Fluid 3D ElevenLabs Orb & Particle Animation Loop
  useEffect(() => {
    let phase = 0;

    const render = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;

      phase += 0.04;

      // 1. Calculate live audio intensity
      let targetLevel = 0;
      if (isSpeaking) {
        const buffer = audioBufferRef.current;
        const audio = audioElement;

        if (buffer && audio && !audio.paused && !audio.ended) {
          const sampleRate = buffer.sampleRate;
          const currentTime = audio.currentTime;
          const currentSample = Math.floor(currentTime * sampleRate);
          const channelData = buffer.getChannelData(0);

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
            targetLevel = Math.min(1, Math.max(0, (rms - 0.008) / 0.16));
          }
        } else {
          // Organic speech modulation
          const s1 = Math.sin(phase * 3.2);
          const s2 = Math.sin(phase * 6.4);
          const raw = Math.max(0, s1 * 0.6 + s2 * 0.4 + 0.2);
          targetLevel = Math.min(1, raw * 0.85);
        }
      } else if (emotion === "listening") {
        targetLevel = 0.25 + Math.sin(phase * 2) * 0.15;
      } else if (emotion === "thinking") {
        targetLevel = 0.35 + Math.sin(phase * 4) * 0.2;
      } else {
        targetLevel = 0.1 + Math.sin(phase * 1.5) * 0.05;
      }

      // Smooth attack/release lerp
      smoothLevelRef.current += (targetLevel - smoothLevelRef.current) * 0.35;
      const level = smoothLevelRef.current;
      setAudioLevel(level);

      // Clear canvas
      ctx.clearRect(0, 0, w, h);

      // 2. Draw outer ambient multi-color glow fields
      const baseRadius = w * 0.28 + level * 25;

      // Outer glow gradient
      const outerGlow = ctx.createRadialGradient(cx, cy, baseRadius * 0.5, cx, cy, baseRadius * 1.8);
      if (isSpeaking) {
        outerGlow.addColorStop(0, "rgba(139, 92, 246, 0.45)");
        outerGlow.addColorStop(0.5, "rgba(236, 72, 153, 0.25)");
        outerGlow.addColorStop(1, "rgba(15, 23, 42, 0)");
      } else if (emotion === "listening") {
        outerGlow.addColorStop(0, "rgba(16, 185, 129, 0.4)");
        outerGlow.addColorStop(0.5, "rgba(6, 182, 212, 0.2)");
        outerGlow.addColorStop(1, "rgba(15, 23, 42, 0)");
      } else if (emotion === "thinking") {
        outerGlow.addColorStop(0, "rgba(59, 130, 246, 0.45)");
        outerGlow.addColorStop(0.5, "rgba(147, 51, 234, 0.25)");
        outerGlow.addColorStop(1, "rgba(15, 23, 42, 0)");
      } else {
        outerGlow.addColorStop(0, "rgba(99, 102, 241, 0.25)");
        outerGlow.addColorStop(0.6, "rgba(168, 85, 247, 0.1)");
        outerGlow.addColorStop(1, "rgba(15, 23, 42, 0)");
      }

      ctx.fillStyle = outerGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, baseRadius * 1.8, 0, Math.PI * 2);
      ctx.fill();

      // 3. Fluid Multi-Frequency Harmonic Waves around the Orb
      const numWaves = 4;
      for (let waveIndex = 0; waveIndex < numWaves; waveIndex++) {
        ctx.save();
        ctx.beginPath();

        const waveOffset = (waveIndex * Math.PI) / 2;
        const waveSpeed = phase * (1.2 + waveIndex * 0.4);
        const waveRadius = baseRadius * (0.92 + waveIndex * 0.08);

        const points = 64;
        for (let i = 0; i <= points; i++) {
          const angle = (i / points) * Math.PI * 2;

          // Harmonic deformation
          const harmonic1 = Math.sin(angle * 3 + waveSpeed + waveOffset);
          const harmonic2 = Math.cos(angle * 5 - waveSpeed * 0.7);
          const harmonic3 = Math.sin(angle * 7 + phase * 2);

          const displacement = (harmonic1 * 0.5 + harmonic2 * 0.3 + harmonic3 * 0.2) * (level * 22 + 4);
          const r = waveRadius + displacement;

          const x = cx + Math.cos(angle) * r;
          const y = cy + Math.sin(angle) * r;

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.closePath();

        // Wave stroke colors
        if (waveIndex === 0) {
          ctx.strokeStyle = `rgba(168, 85, 247, ${0.4 + level * 0.5})`;
          ctx.lineWidth = 3;
        } else if (waveIndex === 1) {
          ctx.strokeStyle = `rgba(236, 72, 153, ${0.35 + level * 0.4})`;
          ctx.lineWidth = 2;
        } else if (waveIndex === 2) {
          ctx.strokeStyle = `rgba(6, 182, 212, ${0.3 + level * 0.5})`;
          ctx.lineWidth = 2.5;
        } else {
          ctx.strokeStyle = `rgba(244, 63, 94, ${0.25 + level * 0.4})`;
          ctx.lineWidth = 1.5;
        }

        ctx.stroke();
        ctx.restore();
      }

      // 4. Draw Core Fluid Iridescent ElevenLabs Orb
      ctx.save();
      ctx.beginPath();

      const corePoints = 48;
      for (let i = 0; i <= corePoints; i++) {
        const angle = (i / corePoints) * Math.PI * 2;
        const deformation =
          Math.sin(angle * 4 + phase * 2.5) * (level * 14 + 2) +
          Math.cos(angle * 6 - phase * 1.8) * (level * 8);
        const r = baseRadius * 0.82 + deformation;

        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.closePath();

      // Fluid Iridescent Gradient for Core Orb
      const coreGrad = ctx.createLinearGradient(
        cx - baseRadius * 0.8,
        cy - baseRadius * 0.8,
        cx + baseRadius * 0.8,
        cy + baseRadius * 0.8
      );

      if (isSpeaking) {
        coreGrad.addColorStop(0, "#c084fc"); // Purple 400
        coreGrad.addColorStop(0.35, "#7c3aed"); // Violet 600
        coreGrad.addColorStop(0.7, "#ec4899"); // Pink 500
        coreGrad.addColorStop(1, "#06b6d4"); // Cyan 500
      } else if (emotion === "listening") {
        coreGrad.addColorStop(0, "#6ee7b7");
        coreGrad.addColorStop(0.5, "#059669");
        coreGrad.addColorStop(1, "#06b6d4");
      } else if (emotion === "thinking") {
        coreGrad.addColorStop(0, "#60a5fa");
        coreGrad.addColorStop(0.5, "#3b82f6");
        coreGrad.addColorStop(1, "#8b5cf6");
      } else {
        coreGrad.addColorStop(0, "#818cf8");
        coreGrad.addColorStop(0.5, "#4f46e5");
        coreGrad.addColorStop(1, "#a855f7");
      }

      ctx.fillStyle = coreGrad;
      ctx.shadowColor = isSpeaking ? "rgba(168, 85, 247, 0.8)" : "rgba(99, 102, 241, 0.5)";
      ctx.shadowBlur = 30 + level * 20;
      ctx.fill();
      ctx.restore();

      // 5. Specular Inner Light Reflection & Dynamic Nucleus
      ctx.save();
      const innerNucleus = ctx.createRadialGradient(
        cx - baseRadius * 0.25,
        cy - baseRadius * 0.25,
        baseRadius * 0.05,
        cx,
        cy,
        baseRadius * 0.7
      );
      innerNucleus.addColorStop(0, "rgba(255, 255, 255, 0.85)");
      innerNucleus.addColorStop(0.3, "rgba(255, 255, 255, 0.25)");
      innerNucleus.addColorStop(1, "rgba(255, 255, 255, 0)");

      ctx.fillStyle = innerNucleus;
      ctx.beginPath();
      ctx.arc(cx, cy, baseRadius * 0.75, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // 6. Orbital Energy Particles
      const numParticles = isSpeaking ? 16 : 8;
      for (let i = 0; i < numParticles; i++) {
        const particleAngle = phase * 0.8 + (i * Math.PI * 2) / numParticles;
        const orbitDist = baseRadius * 1.25 + Math.sin(phase * 2 + i) * 12;
        const px = cx + Math.cos(particleAngle) * orbitDist;
        const py = cy + Math.sin(particleAngle) * orbitDist;

        ctx.beginPath();
        ctx.arc(px, py, 2.5 + level * 2, 0, Math.PI * 2);
        ctx.fillStyle = i % 2 === 0 ? "rgba(168, 85, 247, 0.9)" : "rgba(6, 182, 212, 0.9)";
        ctx.shadowColor = "rgba(255, 255, 255, 0.8)";
        ctx.shadowBlur = 8;
        ctx.fill();
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    animationFrameRef.current = requestAnimationFrame(render);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isSpeaking, audioElement, emotion]);

  // Size mapping
  const sizeMap = {
    sm: "w-44 h-44",
    md: "w-60 h-60",
    lg: "w-72 h-72",
    xl: "w-88 h-88",
  };

  return (
    <div className={cn("relative flex flex-col items-center select-none", className)}>
      {/* Background Holographic Aura Container */}
      <div className="relative z-10 flex flex-col items-center justify-center">
        {/* Canvas Sphere Window */}
        <div
          className={cn(
            "relative rounded-full flex items-center justify-center transition-all duration-500",
            sizeMap[size]
          )}
        >
          {/* ElevenLabs Fluid Voice Canvas */}
          <canvas
            ref={canvasRef}
            width={520}
            height={520}
            className="w-full h-full object-contain"
          />

          {/* Central ElevenLabs AI Icon Badge */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div
              className={cn(
                "p-3.5 rounded-full backdrop-blur-md border border-white/20 shadow-2xl transition-transform duration-300",
                isSpeaking
                  ? "bg-white/20 scale-110 shadow-purple-500/50"
                  : "bg-black/20 scale-100"
              )}
            >
              {isSpeaking ? (
                <Activity className="w-7 h-7 text-white animate-pulse" />
              ) : emotion === "listening" ? (
                <Mic className="w-7 h-7 text-emerald-300 animate-bounce" />
              ) : (
                <Sparkles className="w-7 h-7 text-indigo-200" />
              )}
            </div>
          </div>
        </div>

        {/* Emotion / Mode Status Pill */}
        <div className="mt-2 px-4 py-1.5 rounded-full bg-slate-900/80 backdrop-blur-md border border-purple-500/30 shadow-lg flex items-center gap-2">
          <div
            className={cn(
              "w-2 h-2 rounded-full",
              isSpeaking
                ? "bg-purple-400 animate-ping"
                : emotion === "listening"
                ? "bg-emerald-400 animate-pulse"
                : emotion === "thinking"
                ? "bg-blue-400 animate-spin"
                : "bg-indigo-400"
            )}
          />
          <span className="text-xs font-semibold tracking-wider text-slate-200 uppercase">
            {isSpeaking
              ? "ElevenLabs Voice Active"
              : emotion === "listening"
              ? "Listening to You"
              : emotion === "thinking"
              ? "Processing AI Response"
              : "ElevenLabs AI Ready"}
          </span>
        </div>
      </div>

      {/* Synchronized Voice Frequency Equalizer Bars */}
      {isSpeaking && (
        <div className="mt-5 flex items-center justify-center gap-1.5 h-10 w-full max-w-[280px]">
          {[...Array(20)].map((_, i) => {
            const phaseShift = Math.sin((i / 20) * Math.PI);
            const dynamicHeight = Math.max(15, phaseShift * audioLevel * 100);
            return (
              <div
                key={i}
                className="w-1.5 bg-gradient-to-t from-violet-500 via-fuchsia-500 to-cyan-400 rounded-full transition-all duration-75"
                style={{
                  height: `${dynamicHeight}%`,
                  opacity: 0.4 + audioLevel * 0.6,
                }}
              />
            );
          })}
        </div>
      )}

      {/* Subtitle / Status Text */}
      <div className="mt-4 text-center">
        <p
          className={cn(
            "text-sm font-semibold tracking-wide transition-all duration-300",
            isSpeaking ? "text-purple-400 animate-pulse" : "text-muted-foreground"
          )}
        >
          {isSpeaking && "Lisa is speaking with ElevenLabs Voice..."}
          {!isSpeaking && emotion === "listening" && "Lisa is listening to your answer..."}
          {!isSpeaking && emotion === "thinking" && "Evaluating your response..."}
          {!isSpeaking && emotion === "neutral" && "Ready for the next question"}
        </p>
      </div>
    </div>
  );
}
