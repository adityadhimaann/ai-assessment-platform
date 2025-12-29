import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Volume2, X, Lightbulb, ArrowRight } from "lucide-react";

interface FeedbackOverlayProps {
  isVisible: boolean;
  isCorrect: boolean;
  suggestions: string;
  userAnswer: string;
  onClose: () => void;
  onNext: () => void;
}

export function FeedbackOverlay({ 
  isVisible, 
  isCorrect, 
  suggestions,
  userAnswer,
  onClose,
  onNext 
}: FeedbackOverlayProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-background/50 backdrop-blur-sm">
      <div className={cn(
        "h-full w-full max-w-2xl glass-card-strong border-l border-border/50 p-6 animate-slide-in-right",
        "flex flex-col overflow-y-auto"
      )}>
        <div className="flex items-center justify-between mb-6 sticky top-0 bg-card/80 backdrop-blur-xl pb-4 border-b border-border/30">
          <h2 className="text-xl font-semibold text-foreground">AI Evaluation</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex-1 space-y-6 pb-6">
          {/* Result Badge */}
          <div className="flex justify-center">
            <Badge 
              variant={isCorrect ? "correct" : "incorrect"} 
              className="text-lg px-6 py-2"
            >
              {isCorrect ? "Correct!" : "Needs Improvement"}
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

          {/* Your Answer Section */}
          <div className="bg-muted/30 border border-border/50 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-sm font-semibold text-primary">You</span>
              </div>
              <h3 className="text-sm font-semibold text-foreground">Your Answer</h3>
            </div>
            <p className="text-sm text-foreground/90 leading-relaxed pl-10">
              {userAnswer}
            </p>
          </div>

          {/* AI Suggestions Section */}
          <div className="bg-primary/5 border border-primary/20 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="h-5 w-5 text-primary" />
              <h3 className="text-base font-semibold text-primary">Detailed Feedback & Suggestions</h3>
            </div>
            <div className="text-sm text-foreground/90 leading-relaxed space-y-3">
              {suggestions.split('\n').map((paragraph, index) => (
                paragraph.trim() && (
                  <p key={index} className="text-foreground/80">
                    {paragraph}
                  </p>
                )
              ))}
            </div>
          </div>
        </div>

        <Button 
          variant="glow" 
          size="lg" 
          className="w-full mt-auto sticky bottom-0"
          onClick={onNext}
        >
          Next Question
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
