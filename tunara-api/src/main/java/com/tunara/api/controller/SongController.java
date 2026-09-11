package com.tunara.api.controller;

import com.tunara.api.dto.CreateSongRequest;
import com.tunara.api.dto.SongResponse;
import com.tunara.api.service.SongService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/songs")
public class SongController {

    private final SongService songService;

    public SongController(SongService songService) {
        this.songService = songService;
    }

    @PostMapping
    public ResponseEntity<SongResponse> createSong(
        @Valid @RequestBody CreateSongRequest request
    ) {
        SongResponse response = songService.createSong(request);

        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(response);
    }

    @GetMapping
    public ResponseEntity<List<SongResponse>> getAllSongs() {
        List<SongResponse> songs = songService.getAllSongs();

        return ResponseEntity.ok(songs);
    }

    @GetMapping("/{songId}")
    public ResponseEntity<SongResponse> getSongById(
        @PathVariable UUID songId
    ) {
        SongResponse song = songService.getSongById(songId);

        return ResponseEntity.ok(song);
    }
}