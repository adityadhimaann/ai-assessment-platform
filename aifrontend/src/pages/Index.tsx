import { useState, useCallback, useEffect } from "react";
import { Header } from "@/components/dashboard/Header";
import { QuestionSidebar } from "@/components/dashboard/QuestionSidebar";
import { QuestionCard } from "@/components/dashboard/QuestionCard";
import { WaveformVisualizer } from "@/components/dashboard/WaveformVisualizer";
import { TranscriptBox } from "@/components/dashboard/TranscriptBox";
import { FeedbackOverlay } from "@/components/dashboard/FeedbackOverlay";
import { TopicSelector } from "@/components/dashboard/TopicSelector";
import { ResultsPage } from "@/components/dashboard/ResultsPage";
import { LisaAvatar } from "@/components/dashboard/LisaAvatar";
import { Button } from "@/components/ui/button";
import { Mic, Send, MicOff, RotateCcw } from "lucide-react";
import { useAssessment, type Difficulty } from "@/hooks/useAssessment";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { toast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/api-client";
import lisaGif from "@/assets/lisa.gif";

const TOTAL_QUESTIONS = 10;

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [isLisaSpeaking, setIsLisaSpeaking] = useState(false);
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null);

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
    sessionId,
    startAssessment,
    submitAnswer,
    nextQuestion,
    previousQuestion,
    goToQuestion,
    resetAssessment,
    setEvaluation,
  } = useAssessment();

  const {
    transcript,
    isListening,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
    setTranscript,
  } = useSpeechRecognition();

  const handleStart = useCallback(async (selectedTopic: string, selectedDifficulty: Difficulty) => {
    setTopic(selectedTopic);
    setHasStarted(true);
    await startAssessment();
  }, [setTopic, startAssessment]);

  // Auto-read question when it changes
  useEffect(() => {
    const readQuestion = async () => {
      // Only read if: new question, not answered, not already speaking, and not currently listening
      if (currentQuestion && 
          !currentQuestion.userAnswer && 
          !isLisaSpeaking && 
          !isListening &&
          !transcript) {
        try {
          setIsLisaSpeaking(true);
          
          // Stop any existing audio
          if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
          }
          
          // Get audio from backend
          const audioBlob = await apiClient.readQuestion(currentQuestion.question);
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          
          setCurrentAudio(audio);
          
          audio.onended = () => {
            setIsLisaSpeaking(false);
            URL.revokeObjectURL(audioUrl);
            setCurrentAudio(null);
            
            // Auto-start recording after Lisa finishes speaking
            setTimeout(() => {
              if (isSupported && !isListening && !transcript) {
                startListening();
                toast({
                  title: "Recording Started",
                  description: "Lisa is listening to your answer...",
                });
              }
            }, 500); // Small delay for smooth transition
          };
          
          audio.onerror = () => {
            setIsLisaSpeaking(false);
            URL.revokeObjectURL(audioUrl);
            setCurrentAudio(null);
            console.error("Error playing question audio");
          };
          
          await audio.play();
        } catch (error) {
          console.error("Error reading question:", error);
          setIsLisaSpeaking(false);
        }
      }
    };

    readQuestion();
  }, [currentQuestion?.id]); // Only depend on question ID to prevent loops

  const toggleRecording = useCallback(() => {
    if (!isSupported) {
      toast({
        title: "Not Supported",
        description: "Speech recognition is not supported in your browser. Please use Chrome.",
        variant: "destructive",
      });
      return;
    }

    // Don't allow recording while Lisa is speaking
    if (isLisaSpeaking) {
      toast({
        title: "Please Wait",
        description: "Lisa is still reading the question. Please wait for her to finish.",
        variant: "default",
      });
      return;
    }

    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, isSupported, isLisaSpeaking, startListening, stopListening]);

  const handleSubmit = useCallback(async () => {
    if (!transcript.trim()) {
      toast({
        title: "No Answer Provided",
        description: "Please record your answer before submitting. Speak clearly when the recording starts.",
        variant: "destructive",
      });
      return;
    }
    stopListening();
    await submitAnswer(transcript);
  }, [transcript, stopListening, submitAnswer]);

  const handleNextQuestion = useCallback(async () => {
    resetTranscript();
    
    // Check if we've completed all questions
    if (currentQuestionIndex + 1 >= TOTAL_QUESTIONS) {
      setShowResults(true);
      return;
    }
    
    await nextQuestion();
  }, [resetTranscript, nextQuestion, currentQuestionIndex]);

  const handleReset = useCallback(() => {
    resetAssessment();
    resetTranscript();
    setHasStarted(false);
    setShowResults(false);
  }, [resetAssessment, resetTranscript]);

  const handlePreviousQuestion = useCallback(() => {
    previousQuestion();
    // Load the previous answer into the transcript
    const prevQuestion = questions[currentQuestionIndex - 1];
    if (prevQuestion?.userAnswer) {
      setTranscript(prevQuestion.userAnswer);
    } else {
      resetTranscript();
    }
  }, [previousQuestion, questions, currentQuestionIndex, setTranscript, resetTranscript]);

  const handleGoToQuestion = useCallback((index: number) => {
    goToQuestion(index);
    // Load the answer into the transcript if it exists
    const targetQuestion = questions[index];
    if (targetQuestion?.userAnswer) {
      setTranscript(targetQuestion.userAnswer);
    } else {
      resetTranscript();
    }
  }, [goToQuestion, questions, setTranscript, resetTranscript]);

  // Map questions to sidebar format
  const sidebarQuestions = questions.map((q, index) => ({
    id: q.id,
    title: `Question ${index + 1}`,
    isCorrect: q.isCorrect,
  }));

  // Show topic selector if not started
  if (!hasStarted) {
    return <TopicSelector onStart={handleStart} isLoading={isLoading} />;
  }

  // Show results page if assessment is complete
  if (showResults && sessionId) {
    return <ResultsPage sessionId={sessionId} onStartNew={handleReset} />;
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
            totalQuestions={TOTAL_QUESTIONS}
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
            onSelect={handleGoToQuestion}
          />

          {/* Assessment Area */}
          <main className="flex-1 space-y-4">
            {/* Lisa Avatar - Always visible */}
            {currentQuestion && (
              <div className="flex flex-col items-center gap-4">
                <LisaAvatar 
                  isSpeaking={isLisaSpeaking}
                  message={currentQuestion.question}
                  size="lg"
                />
                
                {/* Question Text - Always visible below avatar */}
                <div className="glass-card p-4 max-w-2xl w-full">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="text-xs font-semibold text-primary">
                        {currentQuestionIndex + 1}
                      </span>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-base font-medium text-foreground mb-1">
                        Question {currentQuestionIndex + 1}
                      </h3>
                      <p className="text-sm text-foreground/9g-relaxed">
                        {currentQuestion.question}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Transcript Box - Show when recording or has transcript */}
            {(isListening || transcript) && (
              <div className="max-w-2xl mx-auto">
                <TranscriptBox transcript={transcript} isActive={isListening} />
              </div>
            )}
            
            {/* Empty Answer Message - Show when stopped recording but no transcript */}
            {!isListening && !transcript && !isLisaSpeaking && !currentQuestion?.userAnswer && questions.length > 0 && (
              <div className="max-w-2xl mx-auto">
                <div className="glass-card p-8 text-center border-2 border-yellow-500/30 bg-yellow-500/5">
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-yellow-500/20 flex items-center justify-center">
                      <span className="text-3xl">🎤</span>
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold text-yellow-500">
                        No Answer Detected
                      </h3>
                      <p className="text-foreground/80">
                        Please speak your answer when recording starts.
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Lisa will automatically start recording after reading the question.
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="lg"
                      onClick={() => {
                        if (isSupported) {
                          startListening();
                          toast({
                            title: "Recording Started",
                            description: "Speak your answer now...",
                          });
                        }
                      }}
                      className="mt-2"
                    >
                      <Mic className="h-4 w-4 mr-2" />
                      Try Recording Again
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-4 max-w-2xl mx-auto">
              {/* Status Messages */}
              <div className="text-center">
                {isLisaSpeaking && (
                  <p className="text-primary animate-pulse text-lg">
                    🎤 Lisa is asking the question...
                  </p>
                )}
                {isListening && !isLisaSpeaking && (
                  <p className="text-primary animate-pulse text-lg">
                    🎙️ Recording your answer...
                  </p>
                )}
                {!isLisaSpeaking && !isListening && !transcript && !currentQuestion?.userAnswer && (
                  <p className="text-muted-foreground">
                    Recording will start automatically...
                  </p>
                )}
              </div>

              {/* Control Buttons */}
              <div className="flex justify-center gap-4">
                {/* Stop Recording Button */}
                {isListening && (
                  <Button
                    variant="destructive"
                    size="lg"
                    onClick={stopListening}
                    className="min-w-[180px]"
                  >
                    <MicOff className="h-5 w-5 mr-2" />
                    Stop Recording
                  </Button>
                )}
                
                {/* Submit Answer Button */}
                {transcript && !currentQuestion?.userAnswer && !isListening && (
                  <Button
                    variant="glow"
                    size="lg"
                    onClick={handleSubmit}
                    className="min-w-[180px] animate-fade-in-up"
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

              {/* Navigation Buttons */}
              {questions.length > 1 && !isLisaSpeaking && (
                <div className="flex justify-center gap-2 pt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handlePreviousQuestion}
                    disabled={currentQuestionIndex === 0 || isEvaluating || isListening}
                  >
                    ← Previous
                  </Button>
                  <span className="text-sm text-muted-foreground flex items-center px-4">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleNextQuestion}
                    disabled={currentQuestionIndex >= questions.length - 1 || !currentQuestion?.userAnswer || isEvaluating || isListening}
                  >
                    Next →
                  </Button>
                </div>
              )}

              {/* Previous Answer Message */}
              {currentQuestion?.userAnswer && (
                <p className="text-center text-sm text-muted-foreground pt-2">
                  ✓ Question already answered. Navigate to continue.
                </p>
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
      {evaluation && currentQuestion && (
        <FeedbackOverlay
          isVisible={!!evaluation}
          isCorrect={evaluation.is_correct}
          suggestions={evaluation.feedback}
          userAnswer={currentQuestion.userAnswer || transcript}
          onClose={() => setEvaluation(null)}
          onNext={handleNextQuestion}
        />
      )}
    </div>
  );
};

export default Index;
