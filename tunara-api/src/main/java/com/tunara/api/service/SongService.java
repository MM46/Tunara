package com.tunara.api.service;

import com.tunara.api.dto.CreateSongRequest;
import com.tunara.api.dto.SongResponse;
import com.tunara.api.entity.GenerationJob;
import com.tunara.api.entity.GenerationJobStatus;
import com.tunara.api.entity.Song;
import com.tunara.api.entity.SongStatus;
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

        GenerationJob generationJob = new GenerationJob();

        generationJob.setSong(savedSong);
        generationJob.setStatus(GenerationJobStatus.PENDING);
        generationJob.setProgress(0);

        generationJobRepository.save(generationJob);

        return toResponse(savedSong);
    }

    @Transactional(readOnly = true)
    public List<SongResponse> getAllSongs() {
        Sort sort = Sort.by(
            Sort.Direction.DESC,
            "createdAt"
        );

        return songRepository.findAll(sort)
            .stream()
            .map(this::toResponse)
            .toList();
    }

    @Transactional(readOnly = true)
    public SongResponse getSongById(UUID songId) {
        Song song = songRepository.findById(songId)
            .orElseThrow(
                () -> new IllegalArgumentException(
                    "Song not found: " + songId
                )
            );

        return toResponse(song);
    }

    private String generateTitle(String prompt) {
        String normalizedPrompt = prompt.trim();

        if (normalizedPrompt.length() <= 60) {
            return normalizedPrompt;
        }

        return normalizedPrompt.substring(0, 57) + "...";
    }

    private SongResponse toResponse(Song song) {
        return new SongResponse(
            song.getId(),
            song.getTitle(),
            song.getPrompt(),
            song.getLyrics(),
            song.getGenre(),
            song.getVoice(),
            song.getLanguage(),
            song.getDurationSeconds(),
            song.getStatus(),
            song.getCoverUrl(),
            song.getMp3Url(),
            song.getWavUrl(),
            song.getCreatedAt(),
            song.getUpdatedAt()
        );
    }
}