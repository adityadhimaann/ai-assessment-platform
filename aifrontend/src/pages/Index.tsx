import { useState, useCallback, useEffect, useMemo } from "react";
import { Header } from "@/components/dashboard/Header";
import { QuestionSidebar } from "@/components/dashboard/QuestionSidebar";
import { FeedbackOverlay } from "@/components/dashboard/FeedbackOverlay";
import { TopicSelector } from "@/components/dashboard/TopicSelector";
import { ResultsPage } from "@/components/dashboard/ResultsPage";
import { HybridLisaAvatar } from "@/components/dashboard/HybridLisaAvatar";
import { ConversationPanel } from "@/components/dashboard/ConversationPanel";
import { Button } from "@/components/ui/button";
import { Mic, Send, MicOff, RotateCcw } from "lucide-react";
import { useAssessment, type Difficulty } from "@/hooks/useAssessment";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { toast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/api-client.ts";
import lisaGif from "@/assets/lisa.gif";

const TOTAL_QUESTIONS = 10;

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [isLisaSpeaking, setIsLisaSpeaking] = useState(false);
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null);
  const [lisaEmotion, setLisaEmotion] = useState<"neutral" | "asking" | "listening" | "thinking" | "happy" | "encouraging">("neutral");

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

  const handleStart = useCallback(async (selectedTopic: string, _selectedDifficulty: Difficulty) => {
    setTopic(selectedTopic);
    setHasStarted(true);
    await startAssessment();
  }, [setTopic, startAssessment]);

  // Auto-read question - PARALLEL audio + video generation for speed!
  useEffect(() => {
    const readQuestion = async () => {
      if (currentQuestion && 
          !currentQuestion.userAnswer && 
          !isLisaSpeaking && 
          !isListening &&
          !transcript) {
        try {
          setIsLisaSpeaking(true);
          setLisaEmotion("asking");
          
          // Stop any existing audio
          if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
          }
          
          // Get audio from ElevenLabs (fast - 2-3s)
          // D-ID video generation happens in parallel in HybridLisaAvatar
          const audioBlob = await apiClient.readQuestion(currentQuestion.question);
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          
          setCurrentAudio(audio);
          
          audio.onended = () => {
            setIsLisaSpeaking(false);
            setLisaEmotion("listening");
            URL.revokeObjectURL(audioUrl);
            setCurrentAudio(null);
            
            // Auto-start recording after Lisa finishes speaking
            setTimeout(() => {
              if (isSupported && !isListening && !transcript) {
                startListening();
                setLisaEmotion("listening");
                toast({
                  title: "Recording Started",
                  description: "Lisa is listening to your answer...",
                });
              }
            }, 500);
          };
          
          audio.onerror = () => {
            setIsLisaSpeaking(false);
            setLisaEmotion("neutral");
            URL.revokeObjectURL(audioUrl);
            setCurrentAudio(null);
            console.error("Error playing question audio");
          };
          
          // Play audio immediately (don't wait for D-ID video)
          await audio.play();
          
        } catch (error) {
          console.error("Error reading question:", error);
          setIsLisaSpeaking(false);
          setLisaEmotion("neutral");
        }
      }
    };

    readQuestion();
  }, [currentQuestion?.id]);

  // Build conversation messages from questions
  const conversationMessages = useMemo(() => {
    const messages: Array<{
      type: "question" | "answer";
      content: string;
      timestamp?: string;
      isCorrect?: boolean;
    }> = [];

    questions.forEach((q, index) => {
      // Add question
      messages.push({
        type: "question",
        content: q.question,
        timestamp: `Q${index + 1}`,
      });

      // Add answer if exists
      if (q.userAnswer) {
        messages.push({
          type: "answer",
          content: q.userAnswer,
          timestamp: `A${index + 1}`,
          isCorrect: q.isCorrect,
        });
      }
    });

    return messages;
  }, [questions]);

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
    setLisaEmotion("thinking");
    await submitAnswer(transcript);
    
    // Show encouraging emotion after evaluation
    setTimeout(() => {
      setLisaEmotion("encouraging");
    }, 1000);
  }, [transcript, stopListening, submitAnswer]);

  const handleNextQuestion = useCallback(async () => {
    resetTranscript();
    setLisaEmotion("neutral");
    
    // Check if we've completed all questions
    if (currentQuestionIndex + 1 >= TOTAL_QUESTIONS) {
      setShowResults(true);
      setLisaEmotion("happy");
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

        {/* Main Content - Split Screen */}
        <div className="flex gap-6">
          {/* Sidebar */}
          <QuestionSidebar
            questions={sidebarQuestions}
            currentQuestionIndex={currentQuestionIndex}
            isCollapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            onSelect={handleGoToQuestion}
          />

          {/* Left Side - Lisa Avatar */}
          <div className="w-[400px] flex-shrink-0">
            <div className="glass-card h-[calc(100vh-200px)] flex flex-col items-center justify-center p-8">
              <HybridLisaAvatar 
                isSpeaking={isLisaSpeaking}
                questionText={currentQuestion?.question}
                emotion={lisaEmotion}
                size="xl"
              />
              
              {/* Lisa's name */}
              <div className="mt-6 text-center">
                <h2 className="text-2xl font-bold text-foreground mb-2">Lisa</h2>
                <p className="text-sm text-muted-foreground">
                  Your AI Interview Assistant
                </p>
              </div>

              {/* Status indicator */}
              <div className="mt-8 w-full space-y-3">
                {isLisaSpeaking && (
                  <div className="flex items-center justify-center gap-2 text-primary animate-pulse">
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce" />
                    <span className="text-sm font-medium">Speaking...</span>
                  </div>
                )}
                {isListening && !isLisaSpeaking && (
                  <div className="flex items-center justify-center gap-2 text-red-500 animate-pulse">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                    <span className="text-sm font-medium">Listening...</span>
                  </div>
                )}
                {!isLisaSpeaking && !isListening && (
                  <div className="flex items-center justify-center gap-2 text-muted-foreground">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/50" />
                    <span className="text-sm">Ready</span>
                  </div>
                )}
              </div>

              {/* Control Buttons */}
              <div className="mt-8 w-full space-y-3">
                {/* Stop Recording Button */}
                {isListening && (
                  <Button
                    variant="destructive"
                    size="lg"
                    onClick={stopListening}
                    className="w-full"
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
                    className="w-full animate-fade-in-up"
                    disabled={isEvaluating}
                  >
                    {isEvaluating ? (
                      <>
                        <img src={lisaGif} alt="Evaluating..." className="h-5 w-5 mr-2" />
                        Evaluating...
                      </>
                    ) : (
                      <>
                        <Send className="h-5 w-5 mr-2" />
                        Submit Answer
                      </>
                    )}
                  </Button>
                )}

                {/* Manual Record Button (if needed) */}
                {!isListening && !transcript && !isLisaSpeaking && !currentQuestion?.userAnswer && (
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => {
                      if (isSupported) {
                        startListening();
                        setLisaEmotion("listening");
                        toast({
                          title: "Recording Started",
                          description: "Speak your answer now...",
                        });
                      }
                    }}
                    className="w-full"
                  >
                    <Mic className="h-5 w-5 mr-2" />
                    Start Recording
                  </Button>
                )}
              </div>

              {/* Navigation Buttons */}
              {questions.length > 1 && !isLisaSpeaking && (
                <div className="mt-6 w-full flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handlePreviousQuestion}
                    disabled={currentQuestionIndex === 0 || isEvaluating || isListening}
                    className="flex-1"
                  >
                    ← Previous
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleNextQuestion}
                    disabled={currentQuestionIndex >= questions.length - 1 || !currentQuestion?.userAnswer || isEvaluating || isListening}
                    className="flex-1"
                  >
                    Next →
                  </Button>
                </div>
              )}

              {/* Browser support warning */}
              {!isSupported && (
                <p className="mt-4 text-center text-xs text-destructive">
                  Speech recognition not supported. Please use Chrome.
                </p>
              )}
            </div>
          </div>

          {/* Right Side - Conversation Panel */}
          <div className="flex-1 min-w-0">
            <div className="h-[calc(100vh-200px)]">
              <ConversationPanel 
                messages={conversationMessages}
                currentTranscript={transcript && !currentQuestion?.userAnswer ? transcript : undefined}
                isListening={isListening}
              />
            </div>
          </div>
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
