import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Volume2, X, Lightbulb, ArrowRight } from "lucide-react";

interface FeedbackOverlayProps {
  isVisible: boolean;
  isCorrect: boolean;
  suggestions: string;
  onClose: () => void;
  onNext: () => void;
}

export function FeedbackOverlay({ 
  isVisible, 
  isCorrect, 
  suggestions, 
  onClose,
  onNext 
}: FeedbackOverlayProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-background/50 backdrop-blur-sm">
      <div className={cn(
        "h-full w-full max-w-md glass-card-strong border-l border-border/50 p-6 animate-slide-in-right",
        "flex flex-col"
      )}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-foreground">AI Evaluation</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex-1 space-y-6">
          {/* Result Badge */}
          <div className="flex justify-center">
            <Badge 
              variant={isCorrect ? "correct" : "incorrect"} 
              className="text-lg px-6 py-2"
            >
              {isCorrect ? "Correct!" : "Incorrect"}
            </Badge>
          </div>

          {/* Audio Feedback */}
          <div className="flex items-center justify-center gap-3 py-4">
            <div className={cn(
              "h-12 w-12 rounded-full flex items-center justify-center",
              "bg-gradient-to-br from-primary/20 to-secondary/20",
              "border border-primary/30"
            )}>
              <div className="relative">
                <Volume2 className="h-5 w-5 text-primary" />
                <span className="absolute inset-0 rounded-full border-2 border-primary animate-pulse-ring" />
              </div>
            </div>
            <p className="text-sm text-muted-foreground">Playing audio feedback...</p>
          </div>

          {/* Suggestions */}
          <div className="bg-primary/5 border border-primary/20 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-medium text-primary">Suggestions</h3>
            </div>
            <p className="text-sm text-foreground/80 leading-relaxed">
              {suggestions}
            </p>
          </div>
        </div>

        <Button 
          variant="glow" 
          size="lg" 
          className="w-full mt-6"
          onClick={onNext}
        >
          Next Question
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
