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
    const { text } = await req.json();
    
    if (!text) {
      throw new Error("Text is required");
    }

    console.log(`Converting text to speech: ${text.substring(0, 50)}...`);

    // Using Web Speech API compatible response
    // For production, you'd integrate with ElevenLabs or similar TTS service
    // For now, return the text to be read by browser's Speech Synthesis
    return new Response(JSON.stringify({ 
      text,
      method: "browser_synthesis" 
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in text-to-speech:", error);
    const message = error instanceof Error ? error.message : "Unknown error";
    return new Response(JSON.stringify({ error: message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
