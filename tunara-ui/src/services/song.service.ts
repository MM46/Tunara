export interface CreateSongRequest {
  prompt: string;
  genre: string;
  voice: string;
  language: string;
  durationSeconds: number;
}

export interface SongResponse {
  id: string;
  title: string;
  prompt: string;
  lyrics: string | null;
  genre: string;
  voice: string;
  language: string;
  durationSeconds: number;
  status: "DRAFT" | "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  coverUrl: string | null;
  mp3Url: string | null;
  wavUrl: string | null;
  createdAt: string;
  updatedAt: string;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export async function createSong(
  request: CreateSongRequest
): Promise<SongResponse> {
  const response = await fetch(`${API_BASE_URL}/api/songs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(
      `Unable to create song. HTTP status: ${response.status}`
    );
  }

  return response.json() as Promise<SongResponse>;
}

export async function getSongs(): Promise<SongResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/songs`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `Unable to retrieve songs. HTTP status: ${response.status}`
    );
  }

  return response.json() as Promise<SongResponse[]>;
}

export async function getSongById(
  songId: string
): Promise<SongResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/songs/${songId}`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `Unable to retrieve song. HTTP status: ${response.status}`
    );
  }

  return response.json() as Promise<SongResponse>;
}