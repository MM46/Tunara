export type GenerationJobStatus =
  | "PENDING"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface GenerationJobResponse {
  id: string;
  songId: string;
  status: GenerationJobStatus;
  progress: number;
  errorMessage: string | null;
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export async function getGenerationJobBySongId(
  songId: string
): Promise<GenerationJobResponse> {
  const response = await fetch(`${API_BASE_URL}/api/generation-jobs/song/${songId}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Unable to retrieve generation job. HTTP status: ${response.status}`);
  }
  return response.json() as Promise<GenerationJobResponse>;
}
