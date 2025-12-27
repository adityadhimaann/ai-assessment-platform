import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // For browser-based STT, we use the Web Speech API on the client side
    // This endpoint is a placeholder for future server-side STT integration
    // (e.g., with Whisper API or ElevenLabs)
    
    const { audio } = await req.json();
    
    console.log("Speech-to-text request received");
    
    // Return guidance to use browser's Web Speech API
    return new Response(JSON.stringify({ 
      message: "Use browser Web Speech API for real-time transcription",
      method: "browser_recognition"
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in speech-to-text:", error);
    const message = error instanceof Error ? error.message : "Unknown error";
    return new Response(JSON.stringify({ error: message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
