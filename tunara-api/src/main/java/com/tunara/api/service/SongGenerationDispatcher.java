package com.tunara.api.service;

import com.tunara.api.client.TunaraAiClient;
import com.tunara.api.dto.AiGenerateSongRequest;
import com.tunara.api.dto.AiGenerateSongResponse;
import com.tunara.api.entity.GenerationJob;
import com.tunara.api.entity.GenerationJobStatus;
import com.tunara.api.entity.Song;
import com.tunara.api.entity.SongStatus;
import com.tunara.api.event.SongGenerationRequestedEvent;
import com.tunara.api.repository.GenerationJobRepository;
import com.tunara.api.repository.SongRepository;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

import java.time.OffsetDateTime;

@Service
public class SongGenerationDispatcher {

    private final TunaraAiClient tunaraAiClient;
    private final SongRepository songRepository;
    private final GenerationJobRepository generationJobRepository;

    public SongGenerationDispatcher(
        TunaraAiClient tunaraAiClient,
        SongRepository songRepository,
        GenerationJobRepository generationJobRepository
    ) {
        this.tunaraAiClient = tunaraAiClient;
        this.songRepository = songRepository;
        this.generationJobRepository = generationJobRepository;
    }

    @Async
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void dispatch(SongGenerationRequestedEvent event) {
        markProcessing(event);

        try {
            AiGenerateSongRequest request = new AiGenerateSongRequest(
                event.songId(),
                event.prompt(),
                event.genre(),
                event.voice(),
                event.language(),
                event.durationSeconds()
            );

            complete(event, tunaraAiClient.generateSong(request));
        } catch (Exception exception) {
            fail(event, exception);
        }
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void markProcessing(SongGenerationRequestedEvent event) {
        Song song = songRepository.findById(event.songId()).orElseThrow();
        GenerationJob job = generationJobRepository
            .findById(event.generationJobId())
            .orElseThrow();

        song.setStatus(SongStatus.PROCESSING);
        job.setStatus(GenerationJobStatus.PROCESSING);
        job.setProgress(10);
        job.setStartedAt(OffsetDateTime.now());
        job.setErrorMessage(null);

        songRepository.save(song);
        generationJobRepository.save(job);
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void complete(
        SongGenerationRequestedEvent event,
        AiGenerateSongResponse response
    ) {
        validateCoreResponse(response);

        Song song = songRepository.findById(event.songId()).orElseThrow();
        GenerationJob job = generationJobRepository
            .findById(event.generationJobId())
            .orElseThrow();

        song.setTitle(response.title().trim());
        song.setLyrics(response.lyrics().trim());
        song.setWavUrl(response.wavUrl().trim());
        song.setMidiUrl(trimToNull(response.midiUrl()));
        song.setLogicPackUrl(trimToNull(response.logicPackUrl()));
        song.setStatus(SongStatus.COMPLETED);

        job.setStatus(GenerationJobStatus.COMPLETED);
        job.setProgress(100);
        job.setCompletedAt(OffsetDateTime.now());
        job.setErrorMessage(null);

        songRepository.save(song);
        generationJobRepository.save(job);
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void fail(
        SongGenerationRequestedEvent event,
        Exception exception
    ) {
        Song song = songRepository.findById(event.songId()).orElseThrow();
        GenerationJob job = generationJobRepository
            .findById(event.generationJobId())
            .orElseThrow();

        song.setStatus(SongStatus.FAILED);
        job.setStatus(GenerationJobStatus.FAILED);

        String message = exception.getMessage();
        String normalizedMessage = message == null
            ? "Generation failed"
            : message;

        job.setErrorMessage(
            normalizedMessage.substring(
                0,
                Math.min(normalizedMessage.length(), 1000)
            )
        );
        job.setCompletedAt(OffsetDateTime.now());

        songRepository.save(song);
        generationJobRepository.save(job);
    }

    private void validateCoreResponse(AiGenerateSongResponse response) {
        if (
            response == null
                || isBlank(response.title())
                || isBlank(response.lyrics())
                || isBlank(response.wavUrl())
        ) {
            throw new IllegalStateException(
                "Tunara AI returned an incomplete audio response"
            );
        }
    }

    private String trimToNull(String value) {
        return isBlank(value) ? null : value.trim();
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
