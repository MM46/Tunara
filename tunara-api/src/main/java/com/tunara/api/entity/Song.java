package com.tunara.api.entity;
import jakarta.persistence.*;
import lombok.Getter; import lombok.NoArgsConstructor; import lombok.Setter;
import java.time.OffsetDateTime; import java.util.UUID;
@Getter @Setter @NoArgsConstructor @Entity @Table(name="song")
public class Song {
 @Id private UUID id;
 @ManyToOne(fetch=FetchType.LAZY) @JoinColumn(name="user_id") private AppUser user;
 @Column(nullable=false,length=255) private String title;
 @Column(nullable=false,columnDefinition="TEXT") private String prompt;
 @Column(columnDefinition="TEXT") private String lyrics;
 @Column(length=100) private String genre;
 @Column(length=100) private String voice;
 @Column(length=50) private String language;
 @Column(name="duration_seconds") private Integer durationSeconds;
 @Enumerated(EnumType.STRING) @Column(nullable=false,length=50) private SongStatus status;
 @Column(name="cover_url",columnDefinition="TEXT") private String coverUrl;
 @Column(name="mp3_url",columnDefinition="TEXT") private String mp3Url;
 @Column(name="wav_url",columnDefinition="TEXT") private String wavUrl;
 @Column(name="midi_url",columnDefinition="TEXT") private String midiUrl;
 @Column(name="logic_pack_url",columnDefinition="TEXT") private String logicPackUrl;
 @Column(name="created_at",nullable=false) private OffsetDateTime createdAt;
 @Column(name="updated_at",nullable=false) private OffsetDateTime updatedAt;
 @PrePersist public void prePersist(){var now=OffsetDateTime.now(); if(id==null)id=UUID.randomUUID(); if(status==null)status=SongStatus.DRAFT; if(createdAt==null)createdAt=now; updatedAt=now;}
 @PreUpdate public void preUpdate(){updatedAt=OffsetDateTime.now();}
}
