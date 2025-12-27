import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold transition-all duration-300",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary: "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive: "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        easy: "border-easy/50 bg-easy/10 text-easy",
        medium: "border-medium/50 bg-medium/10 text-medium",
        hard: "border-hard/50 bg-hard/10 text-hard",
        success: "border-success/50 bg-success/10 text-success",
        correct: "border-success bg-success/20 text-success shadow-[0_0_15px_hsl(var(--success)/0.3)]",
        incorrect: "border-destructive bg-destructive/20 text-destructive shadow-[0_0_15px_hsl(var(--destructive)/0.3)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
