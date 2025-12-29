import { useEffect, useState } from "react";
import { Trophy, TrendingUp, Target, Award, BarChart3, Home, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SessionSummary {
  session_id: string;
  topic: string;
  total_questions: number;
  correct_answers: number;
  incorrect_answers: number;
  average_score: number;
  final_difficulty: string;
  performance_by_difficulty: {
    [key: string]: {
      correct: number;
      total: number;
    };
  };
  score_trend: number[];
}

interface ResultsPageProps {
  sessionId: string;
  onStartNew: () => void;
}

export function ResultsPage({ sessionId, onStartNew }: ResultsPageProps) {
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, [sessionId]);

  const fetchSummary = async () => {
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
      const response = await fetch(`${apiBaseUrl}/session-summary/${sessionId}`);
      
      if (!response.ok) {
        throw new Error("Failed to fetch summary");
      }
      
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error("Error fetching summary:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <img 
            src="/lisa.gif" 
            alt="Loading" 
            className="w-24 h-24 mx-auto object-contain"
          />
          <p className="text-muted-foreground">Calculating your results...</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-muted-foreground">Unable to load results</p>
          <Button onClick={onStartNew}>Start New Assessment</Button>
        </div>
      </div>
    );
  }

  const accuracyPercentage = summary.total_questions > 0 
    ? Math.round((summary.correct_answers / summary.total_questions) * 100)
    : 0;

  const getPerformanceLevel = (score: number) => {
    if (score >= 90) return { label: "Excellent", color: "text-green-500", bg: "bg-green-500/10" };
    if (score >= 80) return { label: "Great", color: "text-blue-500", bg: "bg-blue-500/10" };
    if (score >= 70) return { label: "Good", color: "text-yellow-500", bg: "bg-yellow-500/10" };
    return { label: "Keep Practicing", color: "text-orange-500", bg: "bg-orange-500/10" };
  };

  const performance = getPerformanceLevel(summary.average_score);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4 py-8">
          <div className="flex justify-center">
            <div className="relative">
              <Trophy className="w-20 h-20 text-primary animate-bounce" />
              <div className="absolute inset-0 rounded-full border-4 border-primary animate-pulse-ring" />
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            Assessment Complete!
          </h1>
          <p className="text-xl text-muted-foreground">
            {summary.topic}
          </p>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Average Score */}
          <div className="glass-card p-6 space-y-3">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">Average Score</h3>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-primary">
                {summary.average_score}%
              </div>
              <Badge className={cn("text-sm", performance.bg, performance.color)}>
                {performance.label}
              </Badge>
            </div>
          </div>

          {/* Accuracy */}
          <div className="glass-card p-6 space-y-3">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">Accuracy</h3>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-primary">
                {accuracyPercentage}%
              </div>
              <p className="text-sm text-muted-foreground">
                {summary.correct_answers} of {summary.total_questions} correct
              </p>
            </div>
          </div>

          {/* Final Level */}
          <div className="glass-card p-6 space-y-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">Final Level</h3>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-primary">
                {summary.final_difficulty}
              </div>
              <p className="text-sm text-muted-foreground">
                Difficulty reached
              </p>
            </div>
          </div>
        </div>

        {/* Performance by Difficulty */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-lg">Performance by Difficulty</h3>
          </div>
          
          <div className="space-y-4">
            {Object.entries(summary.performance_by_difficulty).map(([difficulty, stats]) => {
              const percentage = Math.round((stats.correct / stats.total) * 100);
              return (
                <div key={difficulty} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{difficulty}</span>
                    <span className="text-sm text-muted-foreground">
                      {stats.correct}/{stats.total} correct ({percentage}%)
                    </span>
                  </div>
                  <div className="h-3 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={cn(
                        "h-full rounded-full transition-all duration-500",
                        percentage >= 80 ? "bg-green-500" : 
                        percentage >= 60 ? "bg-blue-500" : 
                        "bg-yellow-500"
                      )}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Score Trend */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-lg">Score Progression</h3>
          </div>
          
          <div className="flex items-end gap-2 h-40">
            {summary.score_trend.map((score, index) => {
              const height = (score / 100) * 100;
              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-1">
                  <div className="relative w-full group">
                    <div 
                      className={cn(
                        "w-full rounded-t transition-all duration-300 hover:opacity-80",
                        score >= 80 ? "bg-green-500" : 
                        score >= 60 ? "bg-blue-500" : 
                        "bg-yellow-500"
                      )}
                      style={{ height: `${height}%`, minHeight: "8px" }}
                    />
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-background border border-border rounded px-2 py-1 text-xs whitespace-nowrap">
                      Q{index + 1}: {score}%
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">{index + 1}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <Button 
            variant="glow" 
            size="lg" 
            onClick={onStartNew}
            className="gap-2"
          >
            <Home className="w-4 h-4" />
            Start New Assessment
          </Button>
          <Button 
            variant="outline" 
            size="lg"
            onClick={() => {
              const text = `I just completed an assessment on ${summary.topic} with Lisa AI!\n\nScore: ${summary.average_score}%\nAccuracy: ${accuracyPercentage}%\nQuestions: ${summary.total_questions}`;
              if (navigator.share) {
                navigator.share({ text });
              } else {
                navigator.clipboard.writeText(text);
                alert("Results copied to clipboard!");
              }
            }}
            className="gap-2"
          >
            <Share2 className="w-4 h-4" />
            Share Results
          </Button>
        </div>
      </div>
    </div>
  );
}
