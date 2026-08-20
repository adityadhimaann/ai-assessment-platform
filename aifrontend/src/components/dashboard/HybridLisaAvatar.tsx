import React from "react";
import { ElevenLabsPersonAvatar } from "./ElevenLabsPersonAvatar";

interface HybridLisaAvatarProps {
  isSpeaking: boolean;
  questionText?: string;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  size?: "sm" | "md" | "lg" | "xl";
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  alignment?: any;
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
    <ElevenLabsPersonAvatar
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
