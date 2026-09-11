export interface CreateSongRequest{prompt:string;genre:string;voice:string;language:string;durationSeconds:number;}
export interface SongResponse{id:string;title:string;prompt:string;lyrics:string|null;genre:string;voice:string;language:string;durationSeconds:number;status:"DRAFT"|"PENDING"|"PROCESSING"|"COMPLETED"|"FAILED";coverUrl:string|null;mp3Url:string|null;wavUrl:string|null;midiUrl:string|null;logicPackUrl:string|null;createdAt:string;updatedAt:string;}
const API=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8080";
async function json<T>(url:string,init?:RequestInit):Promise<T>{const r=await fetch(url,init);if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json() as Promise<T>;}
export function createSong(request:CreateSongRequest){return json<SongResponse>(`${API}/api/songs`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(request)});}
export function getSongs(){return json<SongResponse[]>(`${API}/api/songs`,{cache:"no-store"});}
export function getSongById(id:string){return json<SongResponse>(`${API}/api/songs/${id}`,{cache:"no-store"});}
