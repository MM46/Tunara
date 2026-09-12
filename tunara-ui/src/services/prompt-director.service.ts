export interface CreativeBrief {
  original_idea: string;
  safe_reference_translation: string;
  genre: string;
  subgenre: string;
  language: string;
  duration_seconds: number;
  bpm_range: string;
  tonal_direction: string;
  mood: string;
  lyrical_theme: string;
  song_structure: string[];
  instrumentation: string[];
  vocal_direction: string;
  arrangement_direction: string;
  transition_direction: string;
  mix_direction: string;
  negative_constraints: string[];
  lyrics_prompt: string;
  song_planner_prompt: string;
  production_prompt: string;
}

export interface PromptDirectorResponse {
  status: "COMPLETED";
  progress: 100;
  brief: CreativeBrief;
}

interface ImprovePromptRequest {
  idea: string;
  genre?: string;
  language: string;
  duration_seconds: number;
}

export async function improvePrompt(
  request: ImprovePromptRequest
): Promise<PromptDirectorResponse> {
  const response = await fetch("/api/prompt-director", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Prompt Director failed with HTTP ${response.status}`);
  }

  return response.json() as Promise<PromptDirectorResponse>;
}
