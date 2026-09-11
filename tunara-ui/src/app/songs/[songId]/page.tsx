import AppShell from "@/components/layout/app-shell";
import SongDetail from "@/components/song/song-detail";

interface SongDetailPageProps {
  params: Promise<{
    songId: string;
  }>;
}

export default async function SongDetailPage({
  params,
}: SongDetailPageProps) {
  const { songId } = await params;

  return (
    <AppShell>
      <SongDetail songId={songId} />
    </AppShell>
  );
}
