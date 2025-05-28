import sys
import random
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QPushButton, QListWidget, QListWidgetItem, QSplitter,
    QSizePolicy, QSlider, QTabWidget as QSubTabWidget, QStackedWidget
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class MediaTab(QWidget):
    """
    Manages the UI, state, and logic for the Media Tab.
    Includes sub-tabs for Music and Movies, with video playback.
    """

    def __init__(self, parent=None):  # Removed main_window_ref
        super().__init__(parent)

        # --- Defensive Initialization ---
        self.video_display_widget = None
        self.media_display_stack = None
        self.album_art_label = None
        self.player = None
        self._audio_output = None
        # self.player_controls_widget = None # No longer needed to be passed around

        # --- Media-specific State Variables ---
        self.music_media_data = {}
        self.movie_media_data = {}
        self.current_media_type = None
        self.current_media_playing = None
        self.current_album_playing = None
        self.current_artist_playing = "Unknown Artist"
        self.current_song_path = None
        self.current_song_duration_ms = 0
        self.current_song_elapsed_ms = 0
        # self._is_video_fullscreen = False # Removed fullscreen state

        # --- QMediaPlayer Setup ---
        try:
            self.player = QMediaPlayer()
            self._audio_output = QAudioOutput()
            self.player.setAudioOutput(self._audio_output)

            # Video widget will be created and video output set when needed
            self.video_display_widget = QVideoWidget()  # Create it here
            # self.player.setVideoOutput(self.video_display_widget) # Set dynamically

            self.player.positionChanged.connect(self.update_song_progress_from_player)
            self.player.durationChanged.connect(self.update_song_duration_from_player)
            self.player.playbackStateChanged.connect(self.handle_player_state_changed)
            self.player.mediaStatusChanged.connect(self.handle_media_status_changed)
            self.player.errorOccurred.connect(self.handle_player_error)
            print("QMediaPlayer initialized successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to initialize QMediaPlayer or QAudioOutput: {e}")
            self.player = None

        # --- UI Setup ---
        main_media_layout = QHBoxLayout(self)
        main_media_layout.setSpacing(0)
        main_media_layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_list_button = QPushButton("<")
        self.toggle_list_button.setObjectName("ToggleMediaListButton")
        self.toggle_list_button.setCheckable(True)
        self.toggle_list_button.setChecked(True)
        self.toggle_list_button.setFixedWidth(30)
        self.toggle_list_button.clicked.connect(self.toggle_media_list)
        main_media_layout.addWidget(self.toggle_list_button)

        self.media_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.media_splitter.setObjectName("MediaSplitter")
        self.media_splitter.setHandleWidth(2)

        self.media_side_panel = QWidget()
        self.media_side_panel.setObjectName("MediaSidePanel")
        side_panel_main_layout = QVBoxLayout(self.media_side_panel)
        side_panel_main_layout.setContentsMargins(5, 5, 5, 5)
        side_panel_main_layout.setSpacing(5)

        self.media_type_tabs = QSubTabWidget()
        self.media_type_tabs.setObjectName("MediaTypeSubTabs")
        self.media_type_tabs.currentChanged.connect(self.handle_media_type_tab_changed)

        music_list_widget_container = QWidget()
        music_list_layout = QVBoxLayout(music_list_widget_container)
        music_list_layout.setContentsMargins(0, 0, 0, 0);
        music_list_layout.setSpacing(5)
        music_list_layout.addWidget(QLabel("Albums"))
        self.album_list_widget = QListWidget();
        self.album_list_widget.setObjectName("AlbumList")
        self.album_list_widget.itemClicked.connect(self.handle_album_selected)
        music_list_layout.addWidget(self.album_list_widget, 1)
        music_list_layout.addWidget(QLabel("Songs"))
        self.song_list_widget = QListWidget();
        self.song_list_widget.setObjectName("SongList")
        self.song_list_widget.itemClicked.connect(self.music_item_selected)
        music_list_layout.addWidget(self.song_list_widget, 2)
        self.media_type_tabs.addTab(music_list_widget_container, "Music")

        movie_list_widget_container = QWidget()
        movie_list_layout = QVBoxLayout(movie_list_widget_container)
        movie_list_layout.setContentsMargins(0, 0, 0, 0);
        movie_list_layout.setSpacing(5)
        movie_list_layout.addWidget(QLabel("Movies / Videos"))
        self.movie_list_widget = QListWidget();
        self.movie_list_widget.setObjectName("MovieList")
        self.movie_list_widget.itemClicked.connect(self.movie_item_selected)
        movie_list_layout.addWidget(self.movie_list_widget, 1)
        self.media_type_tabs.addTab(movie_list_widget_container, "Movies")

        side_panel_main_layout.addWidget(self.media_type_tabs)
        self.media_splitter.addWidget(self.media_side_panel)

        main_content_panel = QWidget();
        main_content_panel.setObjectName("MediaContentPanel")
        content_layout = QVBoxLayout(main_content_panel)
        content_layout.setContentsMargins(10, 10, 10, 10);
        content_layout.setSpacing(10)
        content_layout.addWidget(QLabel("Media Player"), 0, alignment=Qt.AlignmentFlag.AlignCenter)

        try:
            self.media_display_stack = QStackedWidget()
            self.media_display_stack.setObjectName("MediaDisplayStack")
            self.media_display_stack.setMinimumSize(320, 180)
            self.media_display_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            self.album_art_label = QLabel("Album Art / Poster")
            self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.album_art_label.setStyleSheet(
                "background-color: #333; border: 1px solid #555; color: #888; font-size: 18px;")
            self.media_display_stack.addWidget(self.album_art_label)  # Index 0

            # self.video_display_widget already created
            self.video_display_widget.setStyleSheet("background-color: black;")
            self.media_display_stack.addWidget(self.video_display_widget)  # Index 1

            content_layout.addWidget(self.media_display_stack, 1)
            print("Media display stack created successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to create media display stack or its children: {e}")
            error_label = QLabel("Error: Media display area could not be initialized.")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(error_label, 1)
            self.media_display_stack = None

        self.now_playing_title_label = QLabel("Select Media Item")
        self.now_playing_title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.now_playing_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.now_playing_title_label)

        self.now_playing_artist_label = QLabel("Details")
        self.now_playing_artist_label.setFont(QFont("Arial", 12))
        self.now_playing_artist_label.setStyleSheet("color: #BBB;")
        self.now_playing_artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.now_playing_artist_label)

        self.media_progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.media_progress_slider.setObjectName("MediaProgressSlider")
        self.media_progress_slider.setRange(0, 100);
        self.media_progress_slider.setValue(0)
        self.media_progress_slider.setEnabled(False);
        self.media_progress_slider.setFixedHeight(15)
        self.media_progress_slider.sliderMoved.connect(self.handle_progress_slider_moved)
        self.media_progress_slider.sliderReleased.connect(self.handle_progress_slider_released)
        self.update_progress_slider_style()
        content_layout.addWidget(self.media_progress_slider)

        player_controls_widget = QWidget()
        controls_grid_layout = QGridLayout(player_controls_widget)
        btn_rewind = QPushButton("<< 10s");
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.setObjectName("PlayPauseButton");
        btn_ffwd = QPushButton("10s >>")
        btn_prev = QPushButton("< Prev");
        btn_next = QPushButton("Next >")

        # Fullscreen button removed from here

        btn_rewind.clicked.connect(self.handle_rewind_song);
        self.play_pause_button.clicked.connect(self.handle_play_pause)
        btn_ffwd.clicked.connect(self.handle_ffwd_song);
        btn_prev.clicked.connect(self.handle_prev_full_item)
        btn_next.clicked.connect(self.handle_next_full_item)

        controls_grid_layout.addWidget(btn_prev, 0, 0)
        controls_grid_layout.addWidget(btn_rewind, 0, 1)
        controls_grid_layout.addWidget(self.play_pause_button, 0, 2)
        controls_grid_layout.addWidget(btn_ffwd, 0, 3)
        controls_grid_layout.addWidget(btn_next, 0, 4)
        # controls_grid_layout.addWidget(self.fullscreen_button, 0, 5) # Removed

        for i in range(5): controls_grid_layout.setColumnStretch(i, 1)  # Adjusted to 5 columns
        content_layout.addWidget(player_controls_widget)

        self.media_splitter.addWidget(main_content_panel)  # Changed from self.main_content_panel_ref
        self.media_splitter.setSizes([220, 540])
        main_media_layout.addWidget(self.media_splitter)

        self.load_media_from_directory()

        if self.media_display_stack:
            if self.album_list_widget.count() > 0:
                self.album_list_widget.setCurrentRow(0)
                self.handle_album_selected(self.album_list_widget.item(0))
            elif self.movie_list_widget.count() > 0:
                self.media_type_tabs.setCurrentIndex(1)
                self.movie_list_widget.setCurrentRow(0)
                self.movie_item_selected(self.movie_list_widget.item(0))
            else:
                self.now_playing_title_label.setText("No media found.")
                self.now_playing_artist_label.setText("Check ../gui/media/{music|video} directory")
                self.update_play_pause_button_state()
                self.media_display_stack.setCurrentWidget(self.album_art_label)
        else:
            self.now_playing_title_label.setText("Media display unavailable.")

    def load_media_from_directory(self):
        self.music_media_data = {}
        self.movie_media_data = {}
        if hasattr(self, 'album_list_widget'): self.album_list_widget.clear()
        if hasattr(self, 'movie_list_widget'): self.movie_list_widget.clear()
        try:
            script_dir = Path(__file__).resolve().parent
            base_media_dir = script_dir.parent / "media"
            music_root_dir = base_media_dir / "music"
            video_root_dir = base_media_dir / "video"
            print(f"Scanning for music in: {music_root_dir.resolve()}")
            if not music_root_dir.is_dir():
                print(f"Music directory not found: {music_root_dir}")
                if hasattr(self, 'album_list_widget'): self.album_list_widget.addItem("Music directory not found.")
            else:
                for album_dir in music_root_dir.iterdir():
                    if album_dir.is_dir():
                        album_name = album_dir.name
                        songs_in_album, song_paths_in_album = [], []
                        for song_file in album_dir.iterdir():
                            if song_file.is_file() and song_file.suffix.lower() == ".mp3":
                                songs_in_album.append(song_file.stem)
                                song_paths_in_album.append(str(song_file.resolve()))
                        if songs_in_album:
                            self.music_media_data[album_name] = {"artist": "Various Artists", "songs": songs_in_album,
                                                                 "paths": song_paths_in_album}
                            if hasattr(self, 'album_list_widget'): self.album_list_widget.addItem(album_name)
                if not self.music_media_data and hasattr(self, 'album_list_widget'): self.album_list_widget.addItem(
                    "No music albums found.")
            print(f"Scanning for videos in: {video_root_dir.resolve()}")
            if not video_root_dir.is_dir():
                print(f"Video directory not found: {video_root_dir}")
                if hasattr(self, 'movie_list_widget'): self.movie_list_widget.addItem("Video directory not found.")
            else:
                found_movies = False
                for movie_file in video_root_dir.iterdir():
                    if movie_file.is_file() and movie_file.suffix.lower() in [".mp4", ".mkv", ".avi"]:
                        self.movie_media_data[movie_file.stem] = str(movie_file.resolve())
                        if hasattr(self, 'movie_list_widget'): self.movie_list_widget.addItem(movie_file.stem)
                        found_movies = True
                if not found_movies and hasattr(self, 'movie_list_widget'): self.movie_list_widget.addItem(
                    "No movies found.")
            if not self.music_media_data and not self.movie_media_data: print("No media content found.")
        except Exception as e:
            print(f"Error scanning media directory: {e}")
            if hasattr(self, 'album_list_widget'): self.album_list_widget.addItem("Error scanning media.")
            if hasattr(self, 'movie_list_widget'): self.movie_list_widget.addItem("Error scanning media.")

    def handle_media_type_tab_changed(self, index):
        if not self.player or not self.media_display_stack: return
        self.player.stop()
        # self._is_video_fullscreen = False # No longer needed

        if index == 0:  # Music tab
            self.media_display_stack.setCurrentWidget(self.album_art_label)
            self.player.setVideoOutput(None)
            # if hasattr(self, 'fullscreen_button'): self.fullscreen_button.setEnabled(False); self.fullscreen_button.setChecked(False) # Fullscreen button removed
            self.current_media_type = "music"
            if self.album_list_widget.count() > 0:
                current_album_item = self.album_list_widget.currentItem()
                if not current_album_item:
                    self.album_list_widget.setCurrentRow(0)
                    current_album_item = self.album_list_widget.item(0)
                self.handle_album_selected(current_album_item)
            else:
                self.music_item_selected(None)
        elif index == 1:  # Movies tab
            if self.video_display_widget:
                self.media_display_stack.setCurrentWidget(self.video_display_widget)
                self.player.setVideoOutput(self.video_display_widget)
                # if hasattr(self, 'fullscreen_button'): self.fullscreen_button.setEnabled(True) # Fullscreen button removed
            else:
                self.media_display_stack.setCurrentWidget(self.album_art_label)
                self.player.setVideoOutput(None)
                # if hasattr(self, 'fullscreen_button'): self.fullscreen_button.setEnabled(False); self.fullscreen_button.setChecked(False) # Fullscreen button removed
                print("Error: Video display widget not available.")
            self.current_media_type = "movie"
            if self.movie_list_widget.count() > 0:
                current_movie_item = self.movie_list_widget.currentItem()
                if not current_movie_item:
                    self.movie_list_widget.setCurrentRow(0)
                    current_movie_item = self.movie_list_widget.item(0)
                self.movie_item_selected(current_movie_item, auto_play=False)
            else:
                self.movie_item_selected(None)

    def toggle_media_list(self, checked):
        self.media_side_panel.setVisible(checked)
        self.toggle_list_button.setText("<" if checked else ">")

    def handle_album_selected(self, item):
        if item is None: return
        album_name = item.text()
        self.current_album_playing = album_name
        self.song_list_widget.clear()
        album_data = self.music_media_data.get(album_name, {})
        songs = album_data.get("songs", [])
        for song_name in songs: self.song_list_widget.addItem(song_name)
        if self.song_list_widget.count() > 0:
            self.song_list_widget.setCurrentRow(0)
            self.music_item_selected(self.song_list_widget.item(0), auto_play=False)
        else:
            self.now_playing_title_label.setText("No songs in album")
            self.now_playing_artist_label.setText(album_data.get("artist", "Unknown Artist"))
            if self.media_display_stack: self.media_display_stack.setCurrentWidget(self.album_art_label)
            if self.album_art_label: self.album_art_label.setText(
                f"Art for\n{album_name}" if album_name else "Album Art / Poster")
            self.current_media_playing = None;
            self.current_song_path = None
            if self.player: self.player.setSource(QUrl())
            if hasattr(self, 'media_progress_slider'): self.media_progress_slider.setValue(
                0); self.media_progress_slider.setEnabled(False)
            self.update_play_pause_button_state()

    def music_item_selected(self, item, auto_play=False):
        if item is None:
            self.update_play_pause_button_state();
            return
        song_title = item.text()
        self.current_media_type = "music"
        if self.media_display_stack: self.media_display_stack.setCurrentWidget(self.album_art_label)
        if self.player: self.player.setVideoOutput(None)
        # if hasattr(self, 'fullscreen_button'): self.fullscreen_button.setEnabled(False); self.fullscreen_button.setChecked(False) # Fullscreen button removed
        self.current_media_playing = song_title
        album_name = self.current_album_playing
        artist_name = "Unknown Artist"
        song_index = self.song_list_widget.currentRow()
        if album_name and album_name in self.music_media_data:
            album_info = self.music_media_data[album_name]
            artist_name = album_info.get("artist", "Unknown Artist")
            self.current_song_path = album_info["paths"][song_index] if 0 <= song_index < len(
                album_info.get("paths", [])) else None
        else:
            self.current_song_path = None
        self.current_artist_playing = artist_name
        self.now_playing_title_label.setText(song_title)
        self.now_playing_artist_label.setText(f"{artist_name} - {album_name if album_name else 'Unknown Album'}")
        if self.album_art_label: self.album_art_label.setText(
            f"Art for\n{album_name}" if album_name else "Album Art / Poster")
        self._load_and_play_media(auto_play)

    def movie_item_selected(self, item, auto_play=False):
        if item is None:
            self.update_play_pause_button_state();
            return
        movie_title = item.text()
        self.current_media_type = "movie"
        if self.media_display_stack and self.video_display_widget: self.media_display_stack.setCurrentWidget(
            self.video_display_widget)
        if self.player and self.video_display_widget: self.player.setVideoOutput(self.video_display_widget)
        # if hasattr(self, 'fullscreen_button'): self.fullscreen_button.setEnabled(True) # Fullscreen button removed
        self.current_media_playing = movie_title
        self.current_song_path = self.movie_media_data.get(movie_title)
        self.current_album_playing = None
        self.current_artist_playing = "Movie"
        self.now_playing_title_label.setText(movie_title)
        self.now_playing_artist_label.setText("Video File")
        self._load_and_play_media(auto_play)

    def _load_and_play_media(self, auto_play):
        if not self.player: return
        if self.current_song_path:
            self.player.setSource(QUrl.fromLocalFile(self.current_song_path))
            if hasattr(self, 'media_progress_slider'): self.media_progress_slider.setEnabled(True)
            if auto_play:
                self.player.play()
            else:
                self.player.stop()
            print(f"Loaded: {self.current_media_playing} (Path: {self.current_song_path})")
        else:
            print(f"Error: No path found for {self.current_media_playing}")
            self.player.setSource(QUrl())
            if hasattr(self, 'media_progress_slider'): self.media_progress_slider.setEnabled(False)
        self.update_play_pause_button_state()

    def handle_play_pause(self):
        if not self.player: return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            if self.current_song_path:
                if self.player.source().isEmpty() or self.player.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia or \
                        (
                                self.player.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia and self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState):
                    self.player.setSource(QUrl.fromLocalFile(self.current_song_path))
                self.player.play()
            elif self.current_media_type == "music" and self.song_list_widget.count() > 0:
                self.song_list_widget.setCurrentRow(0)
                self.music_item_selected(self.song_list_widget.item(0), auto_play=True)
            elif self.current_media_type == "movie" and self.movie_list_widget.count() > 0:
                self.movie_list_widget.setCurrentRow(0)
                self.movie_item_selected(self.movie_list_widget.item(0), auto_play=True)

    def update_play_pause_button_state(self):
        if not hasattr(self, 'play_pause_button') or not self.player: return
        play_style = "QPushButton#PlayPauseButton { background-color: #2ECC71; color: black; border: 1px solid #27AE60; font-weight: bold; } QPushButton#PlayPauseButton:hover { background-color: #29B865; }"
        pause_style = "QPushButton#PlayPauseButton { background-color: #F39C12; color: black; border: 1px solid #D35400; font-weight: bold; } QPushButton#PlayPauseButton:hover { background-color: #E67E22; }"
        default_style = "QPushButton#PlayPauseButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; } QPushButton#PlayPauseButton:hover { background-color: #5A5A5A; }"
        state = self.player.playbackState()
        title_prefix = "";
        media_title_to_display = self.current_media_playing if self.current_media_playing else "Select Media Item"
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_button.setText("Pause");
            self.play_pause_button.setStyleSheet(pause_style);
            title_prefix = "Playing: "
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.play_pause_button.setText("Play");
            self.play_pause_button.setStyleSheet(play_style);
            title_prefix = "Paused: "
        else:  # StoppedState
            self.play_pause_button.setText("Play");
            self.play_pause_button.setStyleSheet(default_style if not self.current_media_playing else play_style)
        if self.current_media_playing:
            self.now_playing_title_label.setText(f"{title_prefix}{media_title_to_display}")
        elif self.current_media_type == "music" and self.song_list_widget.count() == 0 and self.album_list_widget.currentItem():
            self.now_playing_title_label.setText("No songs in album")
        elif self.current_media_type == "movie" and self.movie_list_widget.count() == 0:
            self.now_playing_title_label.setText("No movies found")
        else:
            self.now_playing_title_label.setText("Select Media Item")

    def handle_prev_full_item(self):
        target_list, select_action = (self.song_list_widget, lambda item: self.music_item_selected(item,
                                                                                                   auto_play=True)) if self.current_media_type == "music" else \
            (self.movie_list_widget,
             lambda item: self.movie_item_selected(item, auto_play=True)) if self.current_media_type == "movie" else (
            None, None)
        if not target_list: return
        count = target_list.count();
        current_row = target_list.currentRow()
        if count == 0: return
        prev_row = (current_row - 1 + count) % count
        target_list.setCurrentRow(prev_row);
        select_action(target_list.item(prev_row))

    def handle_next_full_item(self):
        target_list, select_action = (self.song_list_widget, lambda item: self.music_item_selected(item,
                                                                                                   auto_play=True)) if self.current_media_type == "music" else \
            (self.movie_list_widget,
             lambda item: self.movie_item_selected(item, auto_play=True)) if self.current_media_type == "movie" else (
            None, None)
        if not target_list: return
        count = target_list.count();
        current_row = target_list.currentRow()
        if count == 0: return
        next_row = (current_row + 1) % count
        target_list.setCurrentRow(next_row);
        select_action(target_list.item(next_row))

    def handle_rewind_song(self):
        if not self.player or self.player.source().isEmpty(): return
        self.player.setPosition(max(0, self.player.position() - 10000))

    def handle_ffwd_song(self):
        if not self.player or self.player.source().isEmpty(): return
        dur = self.player.duration()
        self.player.setPosition(min(dur, self.player.position() + 10000) if dur > 0 else self.player.position() + 10000)

    def update_song_progress_from_player(self, position_ms):
        if hasattr(self,
                   'media_progress_slider') and self.player and self.player.duration() > 0 and not self.media_progress_slider.isSliderDown():
            self.media_progress_slider.setValue(position_ms)
        self.current_song_elapsed_ms = position_ms

    def update_song_duration_from_player(self, duration_ms):
        if hasattr(self, 'media_progress_slider'):
            if duration_ms > 0:
                self.media_progress_slider.setRange(0, duration_ms);
                self.current_song_duration_ms = duration_ms
            else:
                self.media_progress_slider.setRange(0, 100); self.media_progress_slider.setValue(0)

    def handle_player_state_changed(self, state):
        self.update_play_pause_button_state(); print(f"Player state: {state}")

    def handle_media_status_changed(self, status):
        print(f"Media status: {status}")
        if not self.player: return
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.handle_next_full_item()
        elif status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.update_song_duration_from_player(self.player.duration()); self.media_progress_slider.setEnabled(True)
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.now_playing_title_label.setText(
                "Error: Invalid media"); self.current_media_playing = None; self.media_progress_slider.setEnabled(
                False); self.update_play_pause_button_state()
        elif status == QMediaPlayer.MediaStatus.NoMedia:
            self.media_progress_slider.setValue(0); self.media_progress_slider.setRange(0,
                                                                                        100); self.media_progress_slider.setEnabled(
                False)

    def handle_player_error(self, error, error_string=""):
        if not self.player: return
        print(f"Player Error: {error} - {self.player.errorString()}");
        self.now_playing_title_label.setText(f"Playback Error");
        self.current_media_playing = None;
        self.media_progress_slider.setEnabled(False);
        self.update_play_pause_button_state()

    def handle_progress_slider_moved(self, position):
        pass

    def handle_progress_slider_released(self):
        if self.player and not self.player.source().isEmpty(): self.player.setPosition(
            self.media_progress_slider.value()); self.current_song_elapsed_ms = self.media_progress_slider.value()

    def update_progress_slider_style(self):
        if hasattr(self, 'media_progress_slider'):
            self.media_progress_slider.setStyleSheet(
                "QSlider::groove:horizontal{border:1px solid #5A5A5A;height:6px;background:#404040;margin:0px;border-radius:3px}QSlider::handle:horizontal{background:#2ECC71;border:1px solid #27AE60;width:12px;height:12px;margin:-4px 0;border-radius:6px}QSlider::sub-page:horizontal{background:#2ECC71;border:1px solid #27AE60;height:6px;border-radius:3px}QSlider::add-page:horizontal{background:#666;border:1px solid #5A5A5A;height:6px;border-radius:3px}")

    # Fullscreen methods removed as we are not using main_window_ref for OS fullscreen
    # def handle_fullscreen_toggle(self):
    #     pass
    # def restore_layout_after_fullscreen(self):
    #     pass


# --- Standalone Test ---
if __name__ == '__main__':
    app = QApplication(sys.argv)


    class TestMediaTab(MediaTab):
        def __init__(self, parent=None):
            # For standalone test, we don't need main_window_ref if not using its fullscreen methods
            super().__init__(parent=parent)

        def load_media_from_directory(self):
            self.music_media_data = {}
            self.movie_media_data = {}
            script_dir_for_test = Path(__file__).resolve().parent
            base_media_dir_for_test = script_dir_for_test.parent / "media"
            music_root_dir_for_test = base_media_dir_for_test / "music"
            video_root_dir_for_test = base_media_dir_for_test / "video"
            super().load_media_from_directory()  # Call original loader


    dark_palette_test = QPalette()
    # ... (palette setup as before) ...
    app.setPalette(dark_palette_test)
    app.setStyleSheet("""
        QWidget { font-size: 15px; color: #DDD; }
        QPushButton#ToggleMediaListButton { min-width: 25px; max-width: 25px; padding: 5px 2px; font-size: 18px; font-weight: bold; border-radius: 0px; background-color: #303030; border: 1px solid #444; border-left: none; border-right: none; }
        QPushButton { background-color: #4A4A4A; color: #FFF; border: 1px solid #555; padding: 8px 15px; border-radius: 4px; min-height: 30px; }
        QPushButton:hover { background-color: #5A5A5A; }
        QListWidget { background-color: #2A2A2A; border: 1px solid #444; border-radius: 4px; color: #DDD; padding: 5px; }
        QListWidget::item:selected { background-color: #2ECC71; color: black; }
        QWidget#MediaSidePanel { background-color: #303030; border-right: 1px solid #444; }
        QWidget#MediaContentPanel { background-color: #2A2A2A; border-left: 1px solid #444; }
        QSplitter::handle:horizontal { width: 2px; background-color: #555;}
        QTabWidget#MediaTypeSubTabs > QTabBar::tab { 
             min-width: 80px; padding: 8px 10px; font-size: 14px;
             background-color: #353535; color: #BBB; margin-right: 2px;
             border: 1px solid #444; border-bottom: none;
             border-top-left-radius: 4px; border-top-right-radius: 4px;
        }
        QTabWidget#MediaTypeSubTabs > QTabBar::tab:selected {
            background-color: #2A2A2A; color: #FFF;
        }
    """)
    media_tab_widget = TestMediaTab()
    test_window = QMainWindow();
    test_window.setCentralWidget(media_tab_widget);
    test_window.show()
    sys.exit(app.exec())
