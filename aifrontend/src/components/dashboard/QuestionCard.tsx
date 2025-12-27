import { cn } from "@/lib/utils";
import { HelpCircle } from "lucide-react";

interface QuestionCardProps {
  questionNumber: number;
  question: string;
  className?: string;
}

export function QuestionCard({ questionNumber, question, className }: QuestionCardProps) {
  return (
    <div className={cn("glass-card-strong gradient-border rounded-2xl p-8", className)}>
      <div className="flex items-start gap-4">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shrink-0 shadow-lg glow-primary">
          <HelpCircle className="h-6 w-6 text-primary-foreground" />
        </div>
        
        <div className="flex-1">
          <p className="text-xs text-primary uppercase tracking-wider mb-2 font-medium">
            Question {questionNumber}
          </p>
          <h2 className="text-xl font-semibold text-foreground leading-relaxed">
            {question}
          </h2>
        </div>
      </div>
    </div>
  );
}
