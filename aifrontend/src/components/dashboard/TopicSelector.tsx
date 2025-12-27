import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Sparkles, ArrowRight } from "lucide-react";
import type { Difficulty } from "@/hooks/useAssessment";

interface TopicSelectorProps {
  onStart: (topic: string, difficulty: Difficulty) => void;
  isLoading: boolean;
}

const topics = [
  "Artificial Intelligence",
  "Machine Learning",
  "Data Science",
  "Web Development",
  "Cybersecurity",
  "Cloud Computing",
];

const difficulties: { value: Difficulty; label: string; description: string }[] = [
  { value: "easy", label: "Easy", description: "Basic concepts and definitions" },
  { value: "medium", label: "Medium", description: "Application and analysis" },
  { value: "hard", label: "Hard", description: "Complex problem solving" },
];

export function TopicSelector({ onStart, isLoading }: TopicSelectorProps) {
  const [selectedTopic, setSelectedTopic] = useState("Artificial Intelligence");
  const [customTopic, setCustomTopic] = useState("");
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>("medium");

  const handleStart = () => {
    const topic = customTopic.trim() || selectedTopic;
    onStart(topic, selectedDifficulty);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass-card-strong rounded-2xl p-8 max-w-2xl w-full space-y-8 animate-fade-in-up">
        {/* Header */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl font-bold text-foreground">AI Assessment</h1>
          <p className="text-muted-foreground">
            Test your knowledge with AI-powered adaptive questions
          </p>
        </div>

        {/* Topic Selection */}
        <div className="space-y-4">
          <Label className="text-sm font-medium text-foreground">Select Topic</Label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {topics.map((topic) => (
              <button
                key={topic}
                onClick={() => {
                  setSelectedTopic(topic);
                  setCustomTopic("");
                }}
                className={cn(
                  "p-3 rounded-xl text-sm font-medium transition-all duration-200",
                  "border border-border/50 hover:border-primary/50",
                  selectedTopic === topic && !customTopic
                    ? "bg-primary/20 border-primary text-primary"
                    : "bg-background/30 text-foreground/80 hover:bg-background/50"
                )}
              >
                {topic}
              </button>
            ))}
          </div>
          
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-border/50" />
            <span className="text-xs text-muted-foreground">or</span>
            <div className="h-px flex-1 bg-border/50" />
          </div>
          
          <Input
            placeholder="Enter custom topic..."
            value={customTopic}
            onChange={(e) => setCustomTopic(e.target.value)}
            className="bg-background/30 border-border/50"
          />
        </div>

        {/* Difficulty Selection */}
        <div className="space-y-4">
          <Label className="text-sm font-medium text-foreground">Starting Difficulty</Label>
          <div className="grid grid-cols-3 gap-3">
            {difficulties.map((diff) => (
              <button
                key={diff.value}
                onClick={() => setSelectedDifficulty(diff.value)}
                className={cn(
                  "p-4 rounded-xl text-center transition-all duration-200",
                  "border hover:border-primary/50",
                  selectedDifficulty === diff.value
                    ? diff.value === "easy"
                      ? "bg-easy/20 border-easy"
                      : diff.value === "medium"
                      ? "bg-medium/20 border-medium"
                      : "bg-hard/20 border-hard"
                    : "bg-background/30 border-border/50"
                )}
              >
                <Badge
                  variant={diff.value}
                  className="mb-2"
                >
                  {diff.label}
                </Badge>
                <p className="text-xs text-muted-foreground">{diff.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Start Button */}
        <Button
          variant="glow"
          size="lg"
          className="w-full"
          onClick={handleStart}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Sparkles className="h-5 w-5 mr-2 animate-spin" />
              Generating Question...
            </>
          ) : (
            <>
              Start Assessment
              <ArrowRight className="h-5 w-5 ml-2" />
            </>
          )}
        </Button>

        {/* Info */}
        <p className="text-center text-xs text-muted-foreground">
          The AI will adapt difficulty based on your performance
        </p>
      </div>
    </div>
  );
}
