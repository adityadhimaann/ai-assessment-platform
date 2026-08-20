import React from "react";
import { LisaLipSyncAvatar } from "./LisaLipSyncAvatar";

interface HybridLisaAvatarProps {
  isSpeaking: boolean;
  questionText?: string;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  audioElement?: HTMLAudioElement | null;
  onAudioReady?: (audioUrl: string) => void;
  className?: string;
}

export function HybridLisaAvatar({ 
  isSpeaking, 
  emotion = "neutral",
  size = "xl",
  audioElement,
  className
}: HybridLisaAvatarProps) {
  return (
    <LisaLipSyncAvatar
      isSpeaking={isSpeaking}
      audioElement={audioElement}
      emotion={emotion}
      size={size}
      className={className}
    />
  );
}
