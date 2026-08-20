import React, { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";
import lisaRealNeutral from "@/assets/lisa_real_neutral.jpg";

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
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  // Audio PCM and analysis references
  const audioBufferRef = useRef<AudioBuffer | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const smoothMouthRef = useRef(0);
  const smoothLevelRef = useRef(0);

  // Blinking reference
  const lastBlinkRef = useRef(Date.now());
  const nextBlinkIntervalRef = useRef(3500);

  // Load the base real-face photo once
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = lisaRealNeutral;
    img.onload = () => {
      imageRef.current = img;
      setImageLoaded(true);
    };
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

    const render = () => {
      const canvas = canvasRef.current;
      const img = imageRef.current;

      let targetMouth = 0;
      let targetLevel = 0;

      // 1. Calculate continuous speech energy from PCM data
      if (isSpeaking) {
        const buffer = audioBufferRef.current;
        const audio = audioElement;

        if (buffer && audio && !audio.paused && !audio.ended) {
          const sampleRate = buffer.sampleRate;
          const currentTime = audio.currentTime;
          const currentSample = Math.floor(currentTime * sampleRate);
          const channelData = buffer.getChannelData(0);

          // 15ms window around current playback timestamp
          const windowSize = Math.floor(sampleRate * 0.015);
          const start = Math.max(0, currentSample - Math.floor(windowSize / 2));
          const end = Math.min(channelData.length, start + windowSize);

          if (end > start) {
            let sumSq = 0;
            for (let i = start; i < end; i++) {
              const val = channelData[i];
              sumSq += val * val;
            }
            const rms = Math.sqrt(sumSq / (end - start));

            // Smooth continuous normalization
            const rawNormalized = (rms - 0.014) / 0.15;
            targetMouth = Math.min(1, Math.max(0, rawNormalized));
            targetLevel = Math.min(1, Math.max(0, (rms - 0.01) / 0.16));
          }
        } else {
          // Fallback organic speech cadence while decoding
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

      // Smooth attack/release filtering for organic, fluid lip movement (no photo swapping)
      const attackCoeff = targetMouth > smoothMouthRef.current ? 0.7 : 0.35;
      smoothMouthRef.current += (targetMouth - smoothMouthRef.current) * attackCoeff;
      smoothLevelRef.current += (targetLevel - smoothLevelRef.current) * 0.35;

      const mouthOpenAmount = smoothMouthRef.current;
      setAudioLevel(smoothLevelRef.current);

      // 2. Draw real-time morphed face on canvas
      if (canvas && img) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          const w = canvas.width;
          const h = canvas.height;

          // Clear and draw the base high-definition photo
          ctx.clearRect(0, 0, w, h);
          ctx.drawImage(img, 0, 0, w, h);

          // Natural Blinking Logic (every 3-5 seconds, takes ~140ms)
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

          // Render soft natural eyelid blinking over the real eye coordinates
          if (blinkProgress > 0.05) {
            ctx.save();
            ctx.fillStyle = `rgba(215, 180, 168, ${blinkProgress * 0.95})`;
            
            // Left Eye Eyelid
            ctx.beginPath();
            ctx.ellipse(w * 0.424, h * 0.322, w * 0.038, h * 0.016 * blinkProgress, -0.05, 0, Math.PI * 2);
            ctx.fill();

            // Right Eye Eyelid
            ctx.beginPath();
            ctx.ellipse(w * 0.578, h * 0.322, w * 0.038, h * 0.016 * blinkProgress, 0.05, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
          }

          // 3. CONTINUOUS FLUID LIP-SYNC MORPHING (Rendered seamlessly over mouth coordinates)
          if (mouthOpenAmount > 0.01) {
            const centerX = w * 0.502;
            const centerY = h * 0.478;
            const mouthWidth = w * 0.075 + (mouthOpenAmount * w * 0.008);
            const openHeight = mouthOpenAmount * (h * 0.034);

            const leftX = centerX - mouthWidth;
            const rightX = centerX + mouthWidth;
            const upperY = centerY - 1;
            const lowerY = centerY + openHeight;

            ctx.save();

            // Oral Cavity Interior (Deep gradient depth)
            ctx.beginPath();
            ctx.moveTo(leftX, upperY);
            ctx.quadraticCurveTo(centerX, upperY - (openHeight * 0.15), rightX, upperY);
            ctx.quadraticCurveTo(centerX, lowerY + 2, leftX, upperY);
            ctx.closePath();

            const cavityGrad = ctx.createRadialGradient(centerX, centerY, 2, centerX, centerY, openHeight + 10);
            cavityGrad.addColorStop(0, "#2a0408");
            cavityGrad.addColorStop(0.7, "#42080f");
            cavityGrad.addColorStop(1, "#5c0e18");
            ctx.fillStyle = cavityGrad;
            ctx.fill();

            // Upper Teeth Row (Revealed smoothly)
            ctx.beginPath();
            ctx.moveTo(leftX + 4, upperY);
            ctx.quadraticCurveTo(centerX, upperY, rightX - 4, upperY);
            ctx.quadraticCurveTo(centerX, upperY + Math.min(openHeight * 0.45, 6), leftX + 4, upperY);
            ctx.closePath();
            ctx.fillStyle = "rgba(248, 250, 252, 0.95)";
            ctx.fill();

            // Soft Tongue (Visible on larger vowel openings)
            if (mouthOpenAmount > 0.3) {
              ctx.beginPath();
              ctx.ellipse(
                centerX,
                lowerY - (openHeight * 0.25),
                mouthWidth * 0.45,
                openHeight * 0.35,
                0,
                0,
                Math.PI
              );
              ctx.fillStyle = "rgba(225, 29, 72, 0.85)";
              ctx.fill();
            }

            // Lower Lip Contour (Smoothly warped down with speech)
            ctx.beginPath();
            ctx.moveTo(leftX, upperY);
            ctx.quadraticCurveTo(centerX, lowerY + (mouthOpenAmount * 5) + 3, rightX, upperY);
            ctx.quadraticCurveTo(centerX, lowerY, leftX, upperY);
            ctx.closePath();

            const lipGrad = ctx.createLinearGradient(centerX, lowerY, centerX, lowerY + 8);
            lipGrad.addColorStop(0, "rgba(190, 18, 60, 0.95)");
            lipGrad.addColorStop(1, "rgba(225, 29, 72, 0.85)");
            ctx.fillStyle = lipGrad;
            ctx.fill();

            // Upper Lip Contour (Natural cupid's bow)
            ctx.beginPath();
            ctx.moveTo(leftX, upperY);
            ctx.bezierCurveTo(centerX - 10, upperY - 2.5, centerX - 3, upperY + 0.5, centerX, upperY - 0.5);
            ctx.bezierCurveTo(centerX + 3, upperY + 0.5, centerX + 10, upperY - 2.5, rightX, upperY);
            ctx.quadraticCurveTo(centerX, upperY + 1.5, leftX, upperY);
            ctx.closePath();
            ctx.fillStyle = "rgba(190, 18, 60, 0.9)";
            ctx.fill();

            // Soft feathering blur along mouth corners for seamless integration
            ctx.beginPath();
            ctx.arc(leftX, upperY, 3, 0, Math.PI * 2);
            ctx.arc(rightX, upperY, 3, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(159, 18, 57, 0.4)";
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
  }, [isSpeaking, audioElement, imageLoaded]);

  // Size mapping
  const sizeMap = {
    sm: "w-36 h-36",
    md: "w-52 h-52",
    lg: "w-68 h-68",
    xl: "w-80 h-80",
  };

  return (
    <div className={cn("relative flex flex-col items-center select-none", className)}>
      {/* Speech glow aura */}
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

      {/* Main Avatar Container (Completely Rock-Solid & Stable Anchor) */}
      <div className="relative z-10">
        {/* Outer Ring when speaking */}
        {isSpeaking && (
          <div
            className="absolute inset-0 rounded-full border-2 border-primary/40 animate-pulse-ring"
            style={{ transform: "scale(1.06)" }}
          />
        )}

        {/* Circular Face Canvas Container */}
        <div
          className={cn(
            "relative rounded-full overflow-hidden shadow-2xl bg-slate-950",
            sizeMap[size],
            isSpeaking
              ? "border-4 border-primary shadow-primary/40 ring-4 ring-primary/20"
              : "border-4 border-border/70 shadow-xl"
          )}
        >
          {/* Real-time Smooth Lip-Sync Canvas */}
          <canvas
            ref={canvasRef}
            width={600}
            height={600}
            className="w-full h-full object-cover object-center"
          />

          {/* Ambient Speech Lighting */}
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

      {/* Synchronized Voice Audio Waveform Bars */}
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
