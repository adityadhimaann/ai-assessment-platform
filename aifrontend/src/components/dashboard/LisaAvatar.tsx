import React from "react";
import { ElevenLabsAvatar } from "./ElevenLabsAvatar";

interface LisaAvatarProps {
  isSpeaking: boolean;
  message?: string;
  size?: "sm" | "md" | "lg" | "xl";
  audioElement?: HTMLAudioElement | null;
  audioBlob?: Blob | null;
  emotion?: "neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging";
  className?: string;
}

export function LisaAvatar({
  isSpeaking,
  size = "lg",
  audioElement,
  audioBlob,
  emotion = "neutral",
  className,
}: LisaAvatarProps) {
  return (
    <ElevenLabsAvatar
      isSpeaking={isSpeaking}
      audioElement={audioElement}
      audioBlob={audioBlob}
      emotion={emotion}
      size={size}
      className={className}
    />
  );
}
