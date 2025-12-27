import { cn } from "@/lib/utils";

interface ProgressRingProps {
  current: number;
  total: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function ProgressRing({ 
  current, 
  total, 
  size = 48, 
  strokeWidth = 4,
  className 
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const progress = (current / total) * 100;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          stroke="currentColor"
          fill="transparent"
          className="text-muted/30"
        />
        {/* Progress circle with gradient */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          stroke="url(#progressGradient)"
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="transition-all duration-500 ease-out"
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(217 91% 60%)" />
            <stop offset="100%" stopColor="hsl(187 96% 42%)" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute text-xs font-semibold text-foreground">
        {current}/{total}
      </span>
    </div>
  );
}
