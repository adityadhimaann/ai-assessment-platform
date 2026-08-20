import React from "react";
import { LisaLipSyncAvatar, ElevenLabsAlignmentData } from "./LisaLipSyncAvatar";

interface HybridLisaAvatarProps {
  isSpeaking: boolean;
  questionText?: string;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  alignment?: ElevenLabsAlignmentData | null;
  onAudioReady?: (audioUrl: string) => void;
  className?: string;
}

export function HybridLisaAvatar({ 
  isSpeaking, 
  emotion = "neutral",
  size = "xl",
  audioElement,
  audioBlob,
  alignment,
  className
}: HybridLisaAvatarProps) {
  return (
    <LisaLipSyncAvatar
      isSpeaking={isSpeaking}
      audioElement={audioElement}
      audioBlob={audioBlob}
      alignment={alignment}
      emotion={emotion}
      size={size}
      className={className}
    />
  );
}
