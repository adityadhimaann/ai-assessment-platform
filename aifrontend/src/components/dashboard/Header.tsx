import { Badge } from "@/components/ui/badge";
import { ProgressRing } from "./ProgressRing";
import lisaLogo from "@/assets/lisa.png";

interface HeaderProps {
  topic: string;
  difficulty: "easy" | "medium" | "hard";
  currentQuestion: number;
  totalQuestions: number;
}

export function Header({ topic, difficulty, currentQuestion, totalQuestions }: HeaderProps) {
  return (
    <header className="glass-card-strong rounded-xl px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="h-10 w-10 rounded-lg flex items-center justify-center overflow-hidden">
          <img src={lisaLogo} alt="Lisa AI" className="h-full w-full object-contain" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Lisa AI Assessment</p>
          <h1 className="text-lg font-semibold text-foreground">{topic}</h1>
        </div>
      </div>

      <div className="flex items-center gap-8">
        <div className="flex flex-col items-center gap-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Difficulty</p>
          <Badge variant={difficulty} className="capitalize">
            {difficulty}
          </Badge>
        </div>

        <div className="flex flex-col items-center gap-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Progress</p>
          <ProgressRing current={currentQuestion} total={totalQuestions} size={48} />
        </div>
      </div>
    </header>
  );
}
