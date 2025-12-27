import { cn } from "@/lib/utils";
import { Check, X, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Question {
  id: string | number;
  title: string;
  isCorrect: boolean | null;
}

interface QuestionSidebarProps {
  questions: Question[];
  currentQuestionIndex: number;
  isCollapsed: boolean;
  onToggle: () => void;
  onSelect: (index: number) => void;
}

export function QuestionSidebar({ 
  questions, 
  currentQuestionIndex, 
  isCollapsed, 
  onToggle,
  onSelect 
}: QuestionSidebarProps) {
  return (
    <aside className={cn(
      "glass-card rounded-xl transition-all duration-300 flex flex-col",
      isCollapsed ? "w-14" : "w-64"
    )}>
      <div className="p-3 border-b border-border/30 flex items-center justify-between">
        {!isCollapsed && (
          <h2 className="text-sm font-medium text-foreground">Questions</h2>
        )}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={onToggle}
          className="h-8 w-8 ml-auto"
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {questions.map((question, index) => (
          <button
            key={question.id}
            onClick={() => onSelect(index)}
            className={cn(
              "w-full flex items-center gap-3 p-2 rounded-lg transition-all duration-200",
              "hover:bg-muted/50",
              currentQuestionIndex === index && "bg-primary/10 border border-primary/30"
            )}
          >
            <div className={cn(
              "h-6 w-6 rounded-full flex items-center justify-center text-xs font-medium shrink-0",
              question.isCorrect === true && "bg-success/20 text-success",
              question.isCorrect === false && "bg-destructive/20 text-destructive",
              question.isCorrect === null && "bg-muted text-muted-foreground"
            )}>
              {question.isCorrect === true ? (
                <Check className="h-3 w-3" />
              ) : question.isCorrect === false ? (
                <X className="h-3 w-3" />
              ) : (
                index + 1
              )}
            </div>
            
            {!isCollapsed && (
              <span className={cn(
                "text-sm truncate text-left",
                currentQuestionIndex === index 
                  ? "text-foreground font-medium" 
                  : "text-muted-foreground"
              )}>
                {question.title}
              </span>
            )}
          </button>
        ))}
      </div>
    </aside>
  );
}
