package com.tunara.api.service;
import com.tunara.api.dto.*; import com.tunara.api.entity.*; import com.tunara.api.event.SongGenerationRequestedEvent; import com.tunara.api.exception.ResourceNotFoundException; import com.tunara.api.repository.*; import org.springframework.context.ApplicationEventPublisher; import org.springframework.data.domain.Sort; import org.springframework.stereotype.Service; import org.springframework.transaction.annotation.Transactional; import java.util.*;
@Service public class SongService {
 private final SongRepository songs; private final GenerationJobRepository jobs; private final ApplicationEventPublisher events;
 public SongService(SongRepository s,GenerationJobRepository j,ApplicationEventPublisher e){songs=s;jobs=j;events=e;}
 @Transactional public SongResponse createSong(CreateSongRequest r){Song s=new Song();s.setTitle(title(r.prompt()));s.setPrompt(r.prompt().trim());s.setGenre(r.genre().trim());s.setVoice(r.voice().trim());s.setLanguage(r.language().trim());s.setDurationSeconds(r.durationSeconds());s.setStatus(SongStatus.PENDING);s=songs.save(s);GenerationJob j=new GenerationJob();j.setSong(s);j.setStatus(GenerationJobStatus.PENDING);j.setProgress(0);j=jobs.save(j);events.publishEvent(new SongGenerationRequestedEvent(s.getId(),j.getId(),s.getPrompt(),s.getGenre(),s.getVoice(),s.getLanguage(),s.getDurationSeconds()));return response(s);}
 @Transactional(readOnly=true) public List<SongResponse> getAllSongs(){return songs.findAll(Sort.by(Sort.Direction.DESC,"createdAt")).stream().map(this::response).toList();}
 @Transactional(readOnly=true) public SongResponse getSongById(UUID id){return response(songs.findById(id).orElseThrow(()->new ResourceNotFoundException("Song not found: "+id)));}
 private String title(String p){String n=p.trim();return n.length()<=60?n:n.substring(0,57)+"...";}
 private SongResponse response(Song s){return new SongResponse(s.getId(),s.getTitle(),s.getPrompt(),s.getLyrics(),s.getGenre(),s.getVoice(),s.getLanguage(),s.getDurationSeconds(),s.getStatus(),s.getCoverUrl(),s.getMp3Url(),s.getWavUrl(),s.getMidiUrl(),s.getLogicPackUrl(),s.getCreatedAt(),s.getUpdatedAt());}
}
