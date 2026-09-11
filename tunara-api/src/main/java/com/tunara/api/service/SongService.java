package com.tunara.api.service;

import com.tunara.api.dto.CreateSongRequest;
import com.tunara.api.dto.SongResponse;
import com.tunara.api.entity.GenerationJob;
import com.tunara.api.entity.GenerationJobStatus;
import com.tunara.api.entity.Song;
import com.tunara.api.entity.SongStatus;
import com.tunara.api.exception.ResourceNotFoundException;
import com.tunara.api.repository.GenerationJobRepository;
import com.tunara.api.repository.SongRepository;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class SongService {

    private final SongRepository songRepository;
    private final GenerationJobRepository generationJobRepository;

    public SongService(
        SongRepository songRepository,
        GenerationJobRepository generationJobRepository
    ) {
        this.songRepository = songRepository;
        this.generationJobRepository = generationJobRepository;
    }

    @Transactional
    public SongResponse createSong(CreateSongRequest request) {
        Song song = new Song();
        song.setTitle(generateTitle(request.prompt()));
        song.setPrompt(request.prompt().trim());
        song.setGenre(request.genre().trim());
        song.setVoice(request.voice().trim());
        song.setLanguage(request.language().trim());
        song.setDurationSeconds(request.durationSeconds());
        song.setStatus(SongStatus.PENDING);

        Song savedSong = songRepository.save(song);

        GenerationJob job = new GenerationJob();
        job.setSong(savedSong);
        job.setStatus(GenerationJobStatus.PENDING);
        job.setProgress(0);
        generationJobRepository.save(job);

        return toResponse(savedSong);
    }

    @Transactional(readOnly = true)
    public List<SongResponse> getAllSongs() {
        return songRepository.findAll(Sort.by(Sort.Direction.DESC, "createdAt"))
            .stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public SongResponse getSongById(UUID songId) {
        return toResponse(songRepository.findById(songId)
            .orElseThrow(() -> new ResourceNotFoundException("Song not found: " + songId)));
    }

    private String generateTitle(String prompt) {
        String normalized = prompt.trim();
        return normalized.length() <= 60 ? normalized : normalized.substring(0, 57) + "...";
    }

    private SongResponse toResponse(Song song) {
        return new SongResponse(
            song.getId(), song.getTitle(), song.getPrompt(), song.getLyrics(), song.getGenre(),
            song.getVoice(), song.getLanguage(), song.getDurationSeconds(), song.getStatus(),
            song.getCoverUrl(), song.getMp3Url(), song.getWavUrl(), song.getCreatedAt(),
            song.getUpdatedAt()
        );
    }
}
