import React, { useEffect, useState, useRef } from "react";
import { Volume2, VolumeX } from "lucide-react";
import { cn } from "@/lib/utils";

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
  const [mouthSpread, setMouthSpread] = useState(0); // -1 (pucker/O) to 1 (wide smile/E)
  const [blinkState, setBlinkState] = useState(0); // 0 (open) to 1 (closed)
  const [headTilt, setHeadTilt] = useState(0);
  const [pupilX, setPupilX] = useState(0);
  const [pupilY, setPupilY] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);

  // References for Web Audio API & animation loop
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceNodeRef = useRef<MediaElementAudioSourceNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastBlinkTimeRef = useRef<number>(Date.now());
  const nextBlinkIntervalRef = useRef<number>(3000);

  // Filter & lerping state for smooth organic speech motion
  const currentMouthOpenRef = useRef(0);
  const currentMouthSpreadRef = useRef(0);
  const currentLevelRef = useRef(0);

  // Connect Web Audio API to audioElement when available
  useEffect(() => {
    if (!audioElement) return;

    try {
      if (!audioContextRef.current) {
        const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        audioContextRef.current = new AudioCtx();
      }

      const audioCtx = audioContextRef.current;
      if (audioCtx.state === "suspended") {
        audioCtx.resume();
      }

      if (!analyserRef.current) {
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.6;
        analyserRef.current = analyser;

        // Try connecting element if not already connected
        try {
          if (!sourceNodeRef.current) {
            const source = audioCtx.createMediaElementSource(audioElement);
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            sourceNodeRef.current = source;
          }
        } catch {
          // In case element is already connected to another node
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
      phase += 0.05;

      let targetOpen = 0;
      let targetSpread = 0;
      let rawLevel = 0;

      // 1. Calculate mouth shape from audio or natural cadence
      if (isSpeaking) {
        if (analyserRef.current && audioElement && !audioElement.paused) {
          const bufferLength = analyserRef.current.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);
          analyserRef.current.getByteFrequencyData(dataArray);

          // Vowels/bass energy (bins 2-12: ~80Hz - 500Hz)
          let lowSum = 0;
          for (let i = 2; i <= 12; i++) {
            lowSum += dataArray[i];
          }
          const lowAvg = lowSum / 11;

          // Consonants/treble energy (bins 13-35: ~500Hz - 1500Hz)
          let midSum = 0;
          for (let i = 13; i <= 35; i++) {
            midSum += dataArray[i];
          }
          const midAvg = midSum / 23;

          // Overall RMS level
          let totalSum = 0;
          for (let i = 0; i < 40; i++) {
            totalSum += dataArray[i];
          }
          rawLevel = Math.min(1, (totalSum / 40) / 140);

          // Target mouth opening and spread
          targetOpen = Math.min(1, (lowAvg / 130) * 1.2);
          targetSpread = Math.min(1, Math.max(-0.5, ((midAvg - lowAvg * 0.4) / 100)));
        } else {
          // Organic speech simulation pattern (syllable cadences)
          const s1 = Math.sin(phase * 3.8);
          const s2 = Math.sin(phase * 7.2);
          const s3 = Math.cos(phase * 2.1);
          
          // Syllabic modulation (natural pauses between words)
          const wordPulse = Math.max(0, Math.sin(phase * 1.4));
          const openRaw = (Math.max(0, s1 * 0.6 + s2 * 0.3 + 0.3) * wordPulse);
          
          targetOpen = Math.min(1, openRaw * 1.1);
          targetSpread = Math.sin(phase * 2.5) * 0.5;
          rawLevel = targetOpen * 0.8;
        }
      } else {
        // Idle state: slight breathing
        targetOpen = 0;
        targetSpread = emotion === "happy" ? 0.4 : emotion === "encouraging" ? 0.3 : 0;
        rawLevel = 0;
      }

      // Smooth interpolation (lerp) for organic movement
      currentMouthOpenRef.current += (targetOpen - currentMouthOpenRef.current) * 0.38;
      currentMouthSpreadRef.current += (targetSpread - currentMouthSpreadRef.current) * 0.3;
      currentLevelRef.current += (rawLevel - currentLevelRef.current) * 0.35;

      setMouthOpen(currentMouthOpenRef.current);
      setMouthSpread(currentMouthSpreadRef.current);
      setAudioLevel(currentLevelRef.current);

      // 2. Natural Blinking Logic (every 3-5 seconds, takes ~160ms)
      if (now - lastBlinkTimeRef.current > nextBlinkIntervalRef.current) {
        const blinkProgress = (now - lastBlinkTimeRef.current - nextBlinkIntervalRef.current) / 160;
        if (blinkProgress >= 1) {
          lastBlinkTimeRef.current = now;
          nextBlinkIntervalRef.current = 2500 + Math.random() * 3000;
          setBlinkState(0);
        } else {
          // Blink curve: 0 -> 1 -> 0
          const b = Math.sin(blinkProgress * Math.PI);
          setBlinkState(b);
        }
      } else {
        setBlinkState(0);
      }

      // 3. Head & Pupil dynamics
      if (isSpeaking) {
        setHeadTilt(Math.sin(phase * 0.8) * 2.2);
        setPupilX(Math.sin(phase * 0.4) * 1.5);
        setPupilY(Math.cos(phase * 0.5) * 1.0);
      } else if (emotion === "thinking") {
        setHeadTilt(-3);
        setPupilX(3);
        setPupilY(-3);
      } else if (emotion === "listening") {
        setHeadTilt(2);
        setPupilX(0);
        setPupilY(1);
      } else {
        setHeadTilt(Math.sin(phase * 0.3) * 0.8);
        setPupilX(0);
        setPupilY(0);
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
    sm: "w-32 h-32",
    md: "w-48 h-48",
    lg: "w-64 h-64",
    xl: "w-80 h-80",
  };

  // SVG Mouth Morphing Coordinates
  // Center is at (200, 255)
  const mouthWidthPx = 32 + mouthSpread * 14;
  const mouthHeightPx = mouthOpen * 32;
  const leftX = 200 - mouthWidthPx;
  const rightX = 200 + mouthWidthPx;
  const topY = 252 - (mouthOpen * 4);
  const bottomY = 254 + mouthHeightPx;
  const chinDrop = mouthOpen * 5;

  // Eyebrow emotion adjustments
  let leftBrowY = 148;
  let rightBrowY = 148;
  let browCurve = 142;

  if (emotion === "asking") {
    leftBrowY = 142;
    rightBrowY = 140;
    browCurve = 134;
  } else if (emotion === "thinking") {
    leftBrowY = 152;
    rightBrowY = 144;
    browCurve = 144;
  } else if (emotion === "happy" || emotion === "encouraging") {
    leftBrowY = 144;
    rightBrowY = 144;
    browCurve = 136;
  }

  return (
    <div className={cn("relative flex flex-col items-center select-none", className)}>
      {/* Animated surrounding speech glow aura */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {isSpeaking && (
          <>
            <div 
              className="absolute rounded-full bg-gradient-to-r from-blue-500/20 via-purple-500/25 to-pink-500/20 blur-2xl transition-transform duration-100"
              style={{
                width: "115%",
                height: "115%",
                transform: `scale(${1 + audioLevel * 0.15})`,
              }}
            />
            <div 
              className="absolute rounded-full bg-primary/20 blur-xl transition-transform duration-75"
              style={{
                width: "105%",
                height: "105%",
                transform: `scale(${1 + audioLevel * 0.25})`,
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
              style={{ transform: `scale(${1.08 + audioLevel * 0.08})` }}
            />
            <div 
              className="absolute inset-0 rounded-full border-2 border-secondary/40 animate-pulse-ring animation-delay-300"
              style={{ transform: `scale(${1.15 + audioLevel * 0.12})` }}
            />
          </>
        )}

        {/* Circular Avatar Window */}
        <div
          className={cn(
            "relative rounded-full overflow-hidden transition-all duration-300 shadow-2xl bg-gradient-to-b from-slate-900 via-indigo-950 to-slate-950",
            sizeMap[size],
            isSpeaking
              ? "border-4 border-primary shadow-primary/40 ring-4 ring-primary/20"
              : "border-4 border-border/60 shadow-lg"
          )}
          style={{
            transform: `rotate(${headTilt}deg)`,
            transition: "transform 0.15s ease-out, border-color 0.3s ease",
          }}
        >
          {/* Studio Backdrop Lighting */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(99,102,241,0.25)_0%,rgba(15,23,42,0.95)_80%)]" />

          {/* Real-time Fluent SVG Face Engine */}
          <svg
            viewBox="0 0 400 400"
            className="w-full h-full object-cover"
            style={{ transform: "translateY(12px) scale(1.06)" }}
          >
            <defs>
              {/* Skin Tone Gradient */}
              <linearGradient id="lisaSkin" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#fde0d7" />
                <stop offset="60%" stopColor="#fbcfe8" />
                <stop offset="100%" stopColor="#f9a8d4" />
              </linearGradient>

              {/* Hair Gradient */}
              <linearGradient id="lisaHair" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#2e1065" />
                <stop offset="50%" stopColor="#4c1d95" />
                <stop offset="100%" stopColor="#1e1b4b" />
              </linearGradient>

              {/* Lip Gradient */}
              <linearGradient id="lisaLips" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#f43f5e" />
                <stop offset="100%" stopColor="#be123c" />
              </linearGradient>

              {/* Iris Gradient */}
              <radialGradient id="lisaEye" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#38bdf8" />
                <stop offset="60%" stopColor="#0284c7" />
                <stop offset="100%" stopColor="#0c4a6e" />
              </radialGradient>

              {/* Blazer Gradient */}
              <linearGradient id="lisaBlazer" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#0f172a" />
              </linearGradient>

              {/* Soft Shadow */}
              <filter id="softShadow" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" floodOpacity="0.25" />
              </filter>
            </defs>

            {/* Back Hair Layer */}
            <path
              d="M 110 180 C 80 240 85 360 110 400 L 290 400 C 315 360 320 240 290 180 Z"
              fill="url(#lisaHair)"
            />

            {/* Neck & Collar */}
            <path d="M 172 270 L 172 340 L 228 340 L 228 270 Z" fill="#fbcfe8" />
            <path d="M 172 270 L 200 300 L 228 270 Z" fill="#f472b6" opacity="0.4" />

            {/* Professional Jacket / Outfit */}
            <path
              d="M 100 350 L 165 310 L 200 350 L 235 310 L 300 350 L 320 400 L 80 400 Z"
              fill="url(#lisaBlazer)"
              filter="url(#softShadow)"
            />
            {/* White Blouse V-neck */}
            <polygon points="175,315 200,345 225,315" fill="#ffffff" />
            {/* Collar Trim */}
            <path d="M 165 310 L 200 355 L 235 310" stroke="#6366f1" strokeWidth="2.5" fill="none" />

            {/* Head / Face Base Shape (with dynamic chin drop) */}
            <g style={{ transform: `translateY(${chinDrop * 0.4}px)` }}>
              <path
                d={`M 130 180 C 130 110 270 110 270 180 C 270 240 245 ${285 + chinDrop} 200 ${288 + chinDrop} C 155 ${285 + chinDrop} 130 240 130 180 Z`}
                fill="url(#lisaSkin)"
                filter="url(#softShadow)"
              />
              {/* Soft Cheek Blush */}
              <ellipse cx="152" cy="225" rx="14" ry="8" fill="#fb7185" opacity="0.3" />
              <ellipse cx="248" cy="225" rx="14" ry="8" fill="#fb7185" opacity="0.3" />
            </g>

            {/* Nose */}
            <path
              d="M 197 205 Q 200 226 203 226 Q 196 230 192 227"
              stroke="#f472b6"
              strokeWidth="2.5"
              strokeLinecap="round"
              fill="none"
            />

            {/* Eyebrows (Emotion Responsive) */}
            {/* Left Eyebrow */}
            <path
              d={`M 145 ${leftBrowY + 4} Q 165 ${browCurve} 185 ${leftBrowY}`}
              stroke="#311042"
              strokeWidth="3.5"
              strokeLinecap="round"
              fill="none"
            />
            {/* Right Eyebrow */}
            <path
              d={`M 215 ${rightBrowY} Q 235 ${browCurve} 255 ${rightBrowY + 4}`}
              stroke="#311042"
              strokeWidth="3.5"
              strokeLinecap="round"
              fill="none"
            />

            {/* Left Eye */}
            <g transform="translate(162, 182)">
              {/* Eye White */}
              <path d="M -20 0 Q 0 -12 20 0 Q 0 12 -20 0 Z" fill="#ffffff" />
              {/* Iris & Pupil */}
              <g transform={`translate(${pupilX}, ${pupilY})`}>
                <circle cx="0" cy="0" r="7.5" fill="url(#lisaEye)" />
                <circle cx="0" cy="0" r="3.8" fill="#0f172a" />
                {/* Specular Catchlights */}
                <circle cx="-2.5" cy="-2.5" r="2.2" fill="#ffffff" />
                <circle cx="2" cy="2" r="1.2" fill="#ffffff" />
              </g>
              {/* Eyelash Outline */}
              <path d="M -22 -1 Q 0 -14 22 -1" stroke="#1e1b4b" strokeWidth="2.5" fill="none" strokeLinecap="round" />
              {/* Eyelid (Blinking Animation) */}
              <path
                d={`M -22 -1 Q 0 ${-14 + blinkState * 26} 22 -1 L 22 -14 L -22 -14 Z`}
                fill="#fbcfe8"
                opacity={blinkState > 0.05 ? 1 : 0}
              />
              {blinkState > 0.5 && (
                <path d="M -20 0 Q 0 8 20 0" stroke="#4c1d95" strokeWidth="2" fill="none" />
              )}
            </g>

            {/* Right Eye */}
            <g transform="translate(238, 182)">
              {/* Eye White */}
              <path d="M -20 0 Q 0 -12 20 0 Q 0 12 -20 0 Z" fill="#ffffff" />
              {/* Iris & Pupil */}
              <g transform={`translate(${pupilX}, ${pupilY})`}>
                <circle cx="0" cy="0" r="7.5" fill="url(#lisaEye)" />
                <circle cx="0" cy="0" r="3.8" fill="#0f172a" />
                {/* Specular Catchlights */}
                <circle cx="-2.5" cy="-2.5" r="2.2" fill="#ffffff" />
                <circle cx="2" cy="2" r="1.2" fill="#ffffff" />
              </g>
              {/* Eyelash Outline */}
              <path d="M -22 -1 Q 0 -14 22 -1" stroke="#1e1b4b" strokeWidth="2.5" fill="none" strokeLinecap="round" />
              {/* Eyelid (Blinking Animation) */}
              <path
                d={`M -22 -1 Q 0 ${-14 + blinkState * 26} 22 -1 L 22 -14 L -22 -14 Z`}
                fill="#fbcfe8"
                opacity={blinkState > 0.05 ? 1 : 0}
              />
              {blinkState > 0.5 && (
                <path d="M -20 0 Q 0 8 20 0" stroke="#4c1d95" strokeWidth="2" fill="none" />
              )}
            </g>

            {/* REAL-TIME MORPHING LIP-SYNC MOUTH */}
            <g style={{ transform: `translateY(${chinDrop * 0.25}px)` }}>
              {mouthOpen > 0.08 ? (
                /* OPEN MOUTH / SPEAKING VISEME */
                <g>
                  {/* Oral Cavity Interior */}
                  <path
                    d={`M ${leftX} ${topY} Q 200 ${topY - 6} ${rightX} ${topY} Q 200 ${bottomY + 4} ${leftX} ${topY} Z`}
                    fill="#450a0a"
                  />
                  {/* Upper Teeth */}
                  <path
                    d={`M ${leftX + 6} ${topY + 1} Q 200 ${topY + 1} ${rightX - 6} ${topY + 1} L ${rightX - 9} ${topY + Math.min(8, mouthHeightPx * 0.4)} Q 200 ${topY + Math.min(10, mouthHeightPx * 0.45)} ${leftX + 9} ${topY + Math.min(8, mouthHeightPx * 0.4)} Z`}
                    fill="#f8fafc"
                  />
                  {/* Tongue (visible on larger openings) */}
                  {mouthOpen > 0.35 && (
                    <path
                      d={`M ${leftX + 10} ${bottomY - 2} Q 200 ${bottomY - (mouthHeightPx * 0.5)} ${rightX - 10} ${bottomY - 2} Q 200 ${bottomY + 2} ${leftX + 10} ${bottomY - 2} Z`}
                      fill="#fb7185"
                    />
                  )}
                  {/* Upper Lip Contour */}
                  <path
                    d={`M ${leftX - 2} ${topY} Q 185 ${topY - 4} 200 ${topY - 1} Q 215 ${topY - 4} ${rightX + 2} ${topY} Q 200 ${topY + 3} ${leftX - 2} ${topY} Z`}
                    fill="url(#lisaLips)"
                  />
                  {/* Lower Lip Contour */}
                  <path
                    d={`M ${leftX - 2} ${topY} Q 200 ${bottomY + 6} ${rightX + 2} ${topY} Q 200 ${bottomY} ${leftX - 2} ${topY} Z`}
                    fill="url(#lisaLips)"
                  />
                </g>
              ) : (
                /* CLOSED / IDLE NATURAL SMILE */
                <g>
                  {/* Closed Lip Outline */}
                  <path
                    d={`M ${leftX} 252 Q 185 249 200 251 Q 215 249 ${rightX} 252 Q 200 256 ${leftX} 252 Z`}
                    fill="url(#lisaLips)"
                  />
                  <path
                    d={`M ${leftX} 252 Q 200 ${258 + (emotion === 'happy' ? 3 : 1)} ${rightX} 252 Q 200 253 ${leftX} 252 Z`}
                    fill="url(#lisaLips)"
                  />
                  {/* Center Lip Line */}
                  <path
                    d={`M ${leftX + 2} 252 Q 185 250 200 252 Q 215 250 ${rightX - 2} 252`}
                    stroke="#881337"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    fill="none"
                  />
                </g>
              )}
            </g>

            {/* Front Styled Hair & Bangs */}
            <path
              d="M 125 180 C 120 110 280 110 275 180 C 275 160 250 125 200 125 C 150 125 125 160 125 180 Z"
              fill="url(#lisaHair)"
            />
            {/* Left Side Hair Wave */}
            <path
              d="M 130 150 C 110 200 115 290 145 320 C 130 280 135 200 145 165 Z"
              fill="url(#lisaHair)"
            />
            {/* Right Side Hair Wave */}
            <path
              d="M 270 150 C 290 200 285 290 255 320 C 270 280 265 200 255 165 Z"
              fill="url(#lisaHair)"
            />
            {/* Stylish Bangs */}
            <path
              d="M 140 140 Q 180 130 205 160 Q 235 130 265 145 Q 200 115 140 140 Z"
              fill="#3b0764"
              opacity="0.6"
            />
          </svg>
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
