import React from "react";
import { ElevenLabsPersonAvatar } from "./ElevenLabsPersonAvatar";

interface LisaAvatarProps {
  isSpeaking: boolean;
  message?: string;
  size?: "sm" | "md" | "lg" | "xl";
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  alignment?: any;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  className?: string;
}

export function LisaAvatar({
  isSpeaking,
  size = "lg",
  audioElement,
  audioBlob,
  alignment,
  emotion = "neutral",
  className,
}: LisaAvatarProps) {
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
