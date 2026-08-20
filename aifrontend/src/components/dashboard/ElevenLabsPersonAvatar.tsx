import React, { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX, Sparkles, Mic, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import lisaRealNeutral from "@/assets/lisa_real_neutral.jpg";
import lisaRealTalking from "@/assets/lisa_real_talking.jpg";

export interface ElevenLabsAlignmentData {
  characters: string[];
  character_start_times_seconds: number[];
  character_end_times_seconds: number[];
}

interface ElevenLabsPersonAvatarProps {
  isSpeaking: boolean;
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  alignment?: ElevenLabsAlignmentData | null;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function ElevenLabsPersonAvatar({
  isSpeaking,
  audioElement,
  audioBlob,
  alignment,
  emotion = "neutral",
  size = "xl",
  className,
}: ElevenLabsPersonAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const neutralImgRef = useRef<HTMLImageElement | null>(null);
  const talkingImgRef = useRef<HTMLImageElement | null>(null);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  // PCM and timing references
  const audioBufferRef = useRef<AudioBuffer | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const smoothMouthRef = useRef(0);
  const smoothLevelRef = useRef(0);

  // Blinking state
  const lastBlinkRef = useRef(Date.now());
  const nextBlinkIntervalRef = useRef(3200);

  // Preload photorealistic human avatar frames
  useEffect(() => {
    let loadedCount = 0;
    const checkLoaded = () => {
      loadedCount++;
      if (loadedCount >= 2) {
        setImagesLoaded(true);
      }
    };

    const img1 = new Image();
    img1.crossOrigin = "anonymous";
    img1.src = lisaRealNeutral;
    img1.onload = checkLoaded;
    neutralImgRef.current = img1;

    const img2 = new Image();
    img2.crossOrigin = "anonymous";
    img2.src = lisaRealTalking;
    img2.onload = checkLoaded;
    talkingImgRef.current = img2;
  }, []);

  // Decode audio blob into raw PCM waveform for millisecond-accurate audio sync
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

  // Main 60 FPS Canvas Rendering & Real-Time Continuous Lip Morphing Loop
  useEffect(() => {
    let fallbackPhase = 0;

    // Binary search for character in ElevenLabs alignment
    const getCharFromAlignment = (time: number): string => {
      if (!alignment || !alignment.characters || alignment.characters.length === 0) return "";
      const starts = alignment.character_start_times_seconds;
      const ends = alignment.character_end_times_seconds;

      let low = 0;
      let high = starts.length - 1;

      while (low <= high) {
        const mid = (low + high) >> 1;
        if (time >= starts[mid] && time <= ends[mid]) {
          return alignment.characters[mid];
        }
        if (time < starts[mid]) {
          high = mid - 1;
        } else {
          low = mid + 1;
        }
      }
      return "";
    };

    const render = () => {
      const canvas = canvasRef.current;
      const neutralImg = neutralImgRef.current;
      const talkingImg = talkingImgRef.current;

      let targetMouth = 0;
      let targetLevel = 0;

      // 1. Calculate speech viseme & amplitude from ElevenLabs
      if (isSpeaking) {
        const audio = audioElement;
        const currentTime = audio ? audio.currentTime : 0;
        const buffer = audioBufferRef.current;

        // Measure real-time RMS energy
        let rms = 0;
        if (buffer && audio && !audio.paused && !audio.ended) {
          const sampleRate = buffer.sampleRate;
          const currentSample = Math.floor(currentTime * sampleRate);
          const channelData = buffer.getChannelData(0);

          const windowSize = Math.floor(sampleRate * 0.015);
          const start = Math.max(0, currentSample - Math.floor(windowSize / 2));
          const end = Math.min(channelData.length, start + windowSize);

          if (end > start) {
            let sumSq = 0;
            for (let i = start; i < end; i++) {
              const val = channelData[i];
              sumSq += val * val;
            }
            rms = Math.sqrt(sumSq / (end - start));
            targetLevel = Math.min(1, Math.max(0, (rms - 0.008) / 0.16));
          }
        }

        // Check ElevenLabs Character-Level Alignment
        if (alignment && audio && !audio.paused && !audio.ended) {
          const char = getCharFromAlignment(currentTime).toLowerCase();

          if (char) {
            if (["a", "o", "u", "w"].includes(char)) {
              targetMouth = 0.85;
            } else if (["e", "i", "y"].includes(char)) {
              targetMouth = 0.60;
            } else if (["m", "b", "p"].includes(char)) {
              targetMouth = 0.0;
            } else if (["f", "v"].includes(char)) {
              targetMouth = 0.25;
            } else if (["l", "d", "t", "n", "s", "z", "r", "k", "g", "j", "c", "h"].includes(char)) {
              targetMouth = 0.45;
            } else {
              targetMouth = 0.0;
            }

            if (rms > 0) {
              const energyScale = Math.min(1.2, Math.max(0.4, (rms - 0.01) / 0.12));
              targetMouth *= energyScale;
            }
          } else {
            targetMouth = 0;
          }
        } else if (rms > 0) {
          const rawNormalized = (rms - 0.012) / 0.15;
          targetMouth = Math.min(1, Math.max(0, rawNormalized));
        } else {
          fallbackPhase += 0.1;
          const wave1 = Math.sin(fallbackPhase * 3.2);
          const wave2 = Math.sin(fallbackPhase * 6.4);
          const cadence = Math.max(0, Math.sin(fallbackPhase * 1.1));
          const raw = Math.max(0, wave1 * 0.6 + wave2 * 0.4 + 0.15) * cadence;
          targetMouth = Math.min(1, raw * 1.1);
          targetLevel = targetMouth * 0.8;
        }
      } else {
        targetMouth = 0;
        targetLevel = 0;
      }

      // Smooth attack/release filtering
      const attackCoeff = targetMouth > smoothMouthRef.current ? 0.75 : 0.4;
      smoothMouthRef.current += (targetMouth - smoothMouthRef.current) * attackCoeff;
      smoothLevelRef.current += (targetLevel - smoothLevelRef.current) * 0.35;

      const mouthOpen = smoothMouthRef.current;
      setAudioLevel(smoothLevelRef.current);

      // 2. Draw photorealistic human avatar on canvas
      if (canvas && neutralImg && talkingImg && imagesLoaded) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          const w = canvas.width;
          const h = canvas.height;

          // Clear and draw base neutral portrait
          ctx.clearRect(0, 0, w, h);
          ctx.drawImage(neutralImg, 0, 0, w, h);

          // Real-time lip & mouth morphing layer
          if (mouthOpen > 0.02) {
            ctx.save();
            ctx.globalAlpha = Math.min(1, mouthOpen * 1.35);

            // Elliptical mouth mask centered directly on Lisa's lips
            ctx.beginPath();
            ctx.ellipse(w * 0.502, h * 0.485, w * 0.085, h * 0.055, 0, 0, Math.PI * 2);
            ctx.clip();

            ctx.drawImage(talkingImg, 0, 0, w, h);
            ctx.restore();
          }

          // Natural Blinking
          const now = Date.now();
          let blinkProgress = 0;
          if (now - lastBlinkRef.current > nextBlinkIntervalRef.current) {
            const elapsed = now - lastBlinkRef.current - nextBlinkIntervalRef.current;
            if (elapsed > 140) {
              lastBlinkRef.current = now;
              nextBlinkIntervalRef.current = 2800 + Math.random() * 3200;
            } else {
              blinkProgress = Math.sin((elapsed / 140) * Math.PI);
            }
          }

          if (blinkProgress > 0.05) {
            ctx.save();
            ctx.fillStyle = `rgba(215, 180, 168, ${blinkProgress * 0.95})`;

            // Left Eye
            ctx.beginPath();
            ctx.ellipse(w * 0.424, h * 0.322, w * 0.038, h * 0.016 * blinkProgress, -0.05, 0, Math.PI * 2);
            ctx.fill();

            // Right Eye
            ctx.beginPath();
            ctx.ellipse(w * 0.578, h * 0.322, w * 0.038, h * 0.016 * blinkProgress, 0.05, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
          }
        }
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    animationFrameRef.current = requestAnimationFrame(render);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isSpeaking, audioElement, imagesLoaded, alignment]);

  // Size mapping
  const sizeMap = {
    sm: "w-40 h-40",
    md: "w-56 h-56",
    lg: "w-72 h-72",
    xl: "w-88 h-88",
  };

  return (
    <div className={cn("relative flex flex-col items-center select-none", className)}>
      {/* Surrounding ElevenLabs Holographic Glow Rings */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {isSpeaking && (
          <>
            <div
              className="absolute rounded-full bg-gradient-to-r from-purple-600/30 via-pink-600/25 to-cyan-500/25 blur-3xl transition-opacity duration-150"
              style={{
                width: "125%",
                height: "125%",
                opacity: 0.4 + audioLevel * 0.6,
              }}
            />
            <div
              className="absolute rounded-full bg-purple-500/20 blur-xl transition-opacity duration-150"
              style={{
                width: "110%",
                height: "110%",
                opacity: 0.3 + audioLevel * 0.7,
              }}
            />
          </>
        )}
      </div>

      {/* Main Avatar Container */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Pulsing Concentric Outer Ring when speaking */}
        {isSpeaking && (
          <div
            className="absolute inset-0 rounded-full border-2 border-purple-400/50 animate-pulse-ring"
            style={{ transform: "scale(1.05)" }}
          />
        )}

        {/* Circular Avatar Window */}
        <div
          className={cn(
            "relative rounded-full overflow-hidden shadow-2xl transition-all duration-300 bg-slate-950",
            sizeMap[size],
            isSpeaking
              ? "border-4 border-purple-500 shadow-purple-500/50 ring-4 ring-purple-500/30"
              : "border-4 border-slate-700 shadow-xl"
          )}
        >
          {/* Real-time Photorealistic Face Canvas */}
          <canvas
            ref={canvasRef}
            width={640}
            height={640}
            className="w-full h-full object-cover object-center"
          />

          {/* Ambient Speech Lighting Overlay */}
          {isSpeaking && (
            <div
              className="absolute inset-0 bg-gradient-to-t from-purple-900/20 via-transparent to-transparent pointer-events-none"
              style={{ opacity: 0.3 + audioLevel * 0.7 }}
            />
          )}
        </div>

        {/* ElevenLabs Status Pill Badge */}
        <div className="mt-3 px-4 py-1.5 rounded-full bg-slate-900/90 backdrop-blur-md border border-purple-500/40 shadow-lg flex items-center gap-2">
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
          <span className="text-xs font-semibold tracking-wider text-purple-200 uppercase">
            {isSpeaking
              ? "ElevenLabs Voice Speaking"
              : emotion === "listening"
              ? "Listening to You"
              : emotion === "thinking"
              ? "Evaluating Response"
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
                className="w-1.5 bg-gradient-to-t from-purple-500 via-pink-500 to-cyan-400 rounded-full transition-all duration-75"
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
      <div className="mt-3 text-center">
        <p
          className={cn(
            "text-sm font-semibold tracking-wide transition-all duration-300",
            isSpeaking ? "text-purple-400 animate-pulse" : "text-muted-foreground"
          )}
        >
          {isSpeaking && "Lisa is speaking (ElevenLabs Voice)..."}
          {!isSpeaking && emotion === "listening" && "Lisa is listening to your answer..."}
          {!isSpeaking && emotion === "thinking" && "Evaluating your response..."}
          {!isSpeaking && emotion === "neutral" && "Ready for the next question"}
        </p>
      </div>
    </div>
  );
}
