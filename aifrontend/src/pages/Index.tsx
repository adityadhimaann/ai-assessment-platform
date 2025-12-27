import { useState, useCallback, useEffect } from "react";
import { Header } from "@/components/dashboard/Header";
import { QuestionSidebar } from "@/components/dashboard/QuestionSidebar";
import { QuestionCard } from "@/components/dashboard/QuestionCard";
import { WaveformVisualizer } from "@/components/dashboard/WaveformVisualizer";
import { TranscriptBox } from "@/components/dashboard/TranscriptBox";
import { FeedbackOverlay } from "@/components/dashboard/FeedbackOverlay";
import { TopicSelector } from "@/components/dashboard/TopicSelector";
import { Button } from "@/components/ui/button";
import { Mic, Send, MicOff, RotateCcw } from "lucide-react";
import { useAssessment, type Difficulty } from "@/hooks/useAssessment";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { toast } from "@/hooks/use-toast";
import lisaGif from "@/assets/lisa.gif";

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  const {
    topic,
    setTopic,
    difficulty,
    questions,
    currentQuestionIndex,
    currentQuestion,
    isLoading,
    isEvaluating,
    evaluation,
    startAssessment,
    submitAnswer,
    nextQuestion,
    resetAssessment,
  } = useAssessment();

  const {
    transcript,
    isListening,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition();

  const handleStart = useCallback(async (selectedTopic: string, selectedDifficulty: Difficulty) => {
    setTopic(selectedTopic);
    setHasStarted(true);
    await startAssessment();
  }, [setTopic, startAssessment]);

  const toggleRecording = useCallback(() => {
    if (!isSupported) {
      toast({
        title: "Not Supported",
        description: "Speech recognition is not supported in your browser. Please use Chrome.",
        variant: "destructive",
      });
      return;
    }

    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, isSupported, startListening, stopListening]);

  const handleSubmit = useCallback(async () => {
    if (!transcript.trim()) {
      toast({
        title: "No Answer",
        description: "Please record your answer before submitting.",
        variant: "destructive",
      });
      return;
    }
    stopListening();
    await submitAnswer(transcript);
  }, [transcript, stopListening, submitAnswer]);

  const handleNextQuestion = useCallback(async () => {
    resetTranscript();
    await nextQuestion();
  }, [resetTranscript, nextQuestion]);

  const handleReset = useCallback(() => {
    resetAssessment();
    resetTranscript();
    setHasStarted(false);
  }, [resetAssessment, resetTranscript]);

  // Map questions to sidebar format
  const sidebarQuestions = questions.map((q) => ({
    id: q.id,
    title: q.title,
    isCorrect: q.isCorrect,
  }));

  // Show topic selector if not started
  if (!hasStarted) {
    return <TopicSelector onStart={handleStart} isLoading={isLoading} />;
  }

  // Show loading state
  if (isLoading && !currentQuestion) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <img src={lisaGif} alt="Lisa is thinking..." className="h-24 w-24 object-contain" />
          </div>
          <p className="text-muted-foreground">Lisa is generating your first question...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-6 lg:p-8">
      {/* Background gradient effect */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Header
            topic={topic}
            difficulty={difficulty}
            currentQuestion={currentQuestionIndex + 1}
            totalQuestions={10}
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="text-muted-foreground hover:text-foreground"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
        </div>

        {/* Main Content */}
        <div className="flex gap-6">
          {/* Sidebar */}
          <QuestionSidebar
            questions={sidebarQuestions}
            currentQuestionIndex={currentQuestionIndex}
            isCollapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            onSelect={(index) => {/* Can add navigation later */}}
          />

          {/* Assessment Area */}
          <main className="flex-1 space-y-6">
            {/* Question Card */}
            {currentQuestion && (
              <QuestionCard
                questionNumber={currentQuestionIndex + 1}
                question={currentQuestion.question}
              />
            )}

            {/* Voice Input & Transcript */}
            <div className="grid md:grid-cols-2 gap-6">
              <WaveformVisualizer isActive={isListening} />
              <TranscriptBox transcript={transcript} isActive={isListening} />
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center gap-4">
              <Button
                variant={isListening ? "destructive" : "glow"}
                size="lg"
                onClick={toggleRecording}
                className="min-w-[160px]"
                disabled={isEvaluating || !isSupported}
              >
                {isListening ? (
                  <>
                    <MicOff className="h-5 w-5 mr-2" />
                    Stop Recording
                  </>
                ) : (
                  <>
                    <Mic className="h-5 w-5 mr-2" />
                    Start Recording
                  </>
                )}
              </Button>
              
              {transcript && (
                <Button
                  variant="default"
                  size="lg"
                  onClick={handleSubmit}
                  className="min-w-[160px] animate-fade-in-up"
                  disabled={isEvaluating}
                >
                  {isEvaluating ? (
                    <>
                      <img src={lisaGif} alt="Evaluating..." className="h-5 w-5 mr-2" />
                      Lisa is evaluating...
                    </>
                  ) : (
                    <>
                      <Send className="h-5 w-5 mr-2" />
                      Submit Answer
                    </>
                  )}
                </Button>
              )}
            </div>

            {/* Browser support warning */}
            {!isSupported && (
              <p className="text-center text-sm text-destructive">
                Speech recognition is not supported in your browser. Please use Chrome.
              </p>
            )}
          </main>
        </div>
      </div>

      {/* Feedback Overlay */}
      {evaluation && (
        <FeedbackOverlay
          isVisible={!!evaluation}
          isCorrect={evaluation.is_correct}
          suggestions={evaluation.feedback}
          onClose={() => {}}
          onNext={handleNextQuestion}
        />
      )}
    </div>
  );
};

export default Index;
