from entities import *

class HealthBar:
    def __init__(self, json_path, entity, scale_factor=4):
        self.position = pygame.Vector2(0, 0)
        self.json_path = json_path
        self.scale_factor = scale_factor
        self.scaled_frames = []
        self.current_frame = 0
        self.current_time = 0
        self.alive = True
        self.health = entity.health
        self.load_animation(json_path)

     #Load json animation data
    def load_animation(self, json_path):
        try:
            with open(json_path, "r") as f:
                animation_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find animation data file at path: {json_path}")
            return

        #Extract relevant data
        frames_data = animation_data["frames"]
        sprite_sheet_path = animation_data["meta"]["image"]
        sprite_sheet_path = os.path.join(os.path.dirname(json_path), sprite_sheet_path)

        #Load sprite sheet
        try:
            self.sprite_sheet = pygame.image.load(sprite_sheet_path)
        except pygame.error as e:
            print(f"Error loading sprite sheet: {sprite_sheet_path}: {e}")
            return

        #Extract and process frames
        frames = []
        for frame_data in frames_data:
            x = frame_data["frame"]["x"]
            y = frame_data["frame"]["y"]
            w = frame_data["frame"]["w"]
            h = frame_data["frame"]["h"]
            duration = frame_data["duration"]
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w , h))
            frames.append((frame, duration))

        #Scaling
        self.scale_factor = 4
        self.scaled_frames = []
        for frame, duration in frames:
            scaled_frame = pygame.transform.scale(frame, (frame.get_width() * self.scale_factor, frame.get_height() * self.scale_factor))
            self.scaled_frames.append((scaled_frame, duration))

    def update(self, dt):
        pass

        #Update the current frame based on the animation time
        if self.scaled_frames:
            self.current_time += dt * 1000
            frame_duration = self.scaled_frames[self.current_frame][1]
            #Check if we should advance the frame
            if self.current_time >= frame_duration:
                self.current_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.scaled_frames)
    
    def draw(self, screen, x_pos, y_pos):
        if self.scaled_frames:
            frame_surface, _ = self.scaled_frames[self.current_frame]
            screen.blit(frame_surface, (self.position.x, self.position.y))
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (x_pos, y_pos))
