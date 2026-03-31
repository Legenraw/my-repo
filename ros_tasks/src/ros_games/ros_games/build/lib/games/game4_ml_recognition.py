import numpy as np
from typing import Optional, List
from core.base_game_engine import BaseGameEngine
from controllers.vehicle_controller import GameState
from entities.image_data import ImageData
from config import Config
import random


class Game4MLRecognition(BaseGameEngine):
    """Game 4: ML Dataset Recognition

    Images from ML datasets (MNIST, etc.) spawn randomly and remain visible
    for a limited duration. The vehicle must navigate and use ML models to
    identify the images. Points are awarded for correct classifications.

    State Information for Controller:
        - vehicle_position, velocity, orientation (standard)
        - screen_frame: Current rendered frame as numpy array (H, W, 3)
        - active_images: List of currently visible ImageData objects
        - current_score: Current score

    The controller can process the screen frame with ML models to classify
    images and earn points.
    """

    def __init__(self, config: Optional[Config] = None, headless: Optional[bool] = None):
        super().__init__(config, headless)

        # Game 4 specific config
        self.dataset_name = self.config.game4_config['dataset']
        self.dataset_path = self.config.game4_config.get('dataset_path', './datasets/mnist')
        self.image_display_size = tuple(self.config.game4_config['image_display_size'])
        self.image_duration = self.config.game4_config['image_duration']
        self.max_images = self.config.game4_config['max_images']
        self.spawn_interval = self.config.game4_config['spawn_interval']
        self.points_per_correct = self.config.game4_config['points_per_correct']
        self.episode_duration = self.config.game4_config['episode_duration']

        # Override max_time with episode duration
        self.max_time = self.episode_duration

        # Game state
        self.active_images: List[ImageData] = []
        self.score = 0
        self.next_spawn_time = 0.0
        self.image_counter = 0

        # Dataset
        self.dataset_images = None
        self.dataset_labels = None
        self._load_dataset()

        # Stats
        self.correct_identifications = 0
        self.incorrect_identifications = 0

    def get_game_mode(self) -> str:
        return "ml_recognition"

    def _load_dataset(self):
        """Load dataset based on configuration.

        Loads actual MNIST dataset if available, otherwise falls back to synthetic.
        """
        if self.dataset_name == "mnist":
            try:
                # Try to load real MNIST using torchvision
                import torch
                from torchvision import datasets, transforms

                print("Loading MNIST dataset...")

                # Download MNIST to dataset_path
                mnist = datasets.MNIST(
                    root=self.dataset_path,
                    train=True,
                    download=True,
                    transform=transforms.ToTensor()
                )

                # Sample subset for performance (use first 500 images)
                num_samples = min(500, len(mnist))
                indices = np.random.choice(len(mnist), num_samples, replace=False)

                self.dataset_images = []
                self.dataset_labels = []

                for idx in indices:
                    img, label = mnist[int(idx)]
                    # Convert tensor to numpy and scale to 0-255
                    img_np = (img.squeeze().numpy() * 255).astype(np.uint8)
                    self.dataset_images.append(img_np)
                    self.dataset_labels.append(label)

                self.dataset_images = np.array(self.dataset_images)
                self.dataset_labels = np.array(self.dataset_labels)

                print(f"Loaded {len(self.dataset_images)} MNIST images")

            except ImportError:
                print("PyTorch not available, trying TensorFlow...")
                try:
                    import tensorflow as tf

                    # Load MNIST using TensorFlow
                    (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()

                    # Sample subset
                    num_samples = min(500, len(x_train))
                    indices = np.random.choice(len(x_train), num_samples, replace=False)

                    self.dataset_images = x_train[indices]
                    self.dataset_labels = y_train[indices]

                    print(f"Loaded {len(self.dataset_images)} MNIST images")

                except ImportError:
                    print("Neither PyTorch nor TensorFlow available. Using synthetic digits.")
                    self.dataset_images, self.dataset_labels = self._generate_synthetic_mnist(100)
        else:
            # Default: random noise images
            self.dataset_images = np.random.randint(0, 255, (100, 28, 28), dtype=np.uint8)
            self.dataset_labels = np.random.randint(0, 10, 100)

    def _generate_synthetic_mnist(self, count: int):
        """Generate better synthetic digit-like images.

        Creates digit-like patterns that resemble actual handwritten digits.
        Users can replace with actual MNIST loading.

        Args:
            count: Number of images to generate

        Returns:
            Tuple of (images, labels) arrays
        """
        images = []
        labels = []

        for i in range(count):
            label = i % 10
            img = np.zeros((28, 28), dtype=np.uint8)

            if label == 0:
                # Draw "0" - oval shape
                y, x = np.ogrid[:28, :28]
                # Outer oval
                mask = ((x - 14)**2 / 49) + ((y - 14)**2 / 81) <= 1
                img[mask] = 255
                # Inner oval (hollow)
                mask_inner = ((x - 14)**2 / 25) + ((y - 14)**2 / 49) <= 1
                img[mask_inner] = 0

            elif label == 1:
                # Draw "1" - vertical line with slight angle
                img[4:24, 13:15] = 255
                img[4:8, 11:13] = 255  # Top angle

            elif label == 2:
                # Draw "2" - top curve, middle, bottom
                img[6:10, 8:20] = 255  # Top horizontal
                img[6:14, 16:20] = 255  # Right curve
                img[12:16, 8:20] = 255  # Middle horizontal
                img[14:22, 8:12] = 255  # Left bottom
                img[20:24, 8:20] = 255  # Bottom horizontal

            elif label == 3:
                # Draw "3" - two curves on right
                img[6:10, 10:20] = 255  # Top horizontal
                img[6:14, 16:20] = 255  # Upper right
                img[12:16, 10:20] = 255  # Middle horizontal
                img[14:22, 16:20] = 255  # Lower right
                img[20:24, 10:20] = 255  # Bottom horizontal

            elif label == 4:
                # Draw "4" - vertical on right, angled on left
                img[4:20, 8:12] = 255  # Left vertical
                img[12:16, 8:20] = 255  # Horizontal
                img[4:24, 16:20] = 255  # Right vertical

            elif label == 5:
                # Draw "5" - top, middle curve
                img[6:10, 8:20] = 255  # Top horizontal
                img[6:14, 8:12] = 255  # Left upper
                img[12:16, 8:20] = 255  # Middle horizontal
                img[14:22, 16:20] = 255  # Right lower
                img[20:24, 8:20] = 255  # Bottom horizontal

            elif label == 6:
                # Draw "6" - circle with opening at top right
                y, x = np.ogrid[:28, :28]
                mask = ((x - 13)**2 + (y - 15)**2) <= 64
                img[mask] = 255
                mask_inner = ((x - 13)**2 + (y - 15)**2) <= 36
                img[mask_inner] = 0
                img[6:14, 14:20] = 0  # Opening at top

            elif label == 7:
                # Draw "7" - top horizontal and diagonal
                img[6:10, 8:20] = 255  # Top horizontal
                for i in range(18):
                    y = 10 + i
                    x = 18 - i
                    if 0 <= y < 28 and 0 <= x < 28:
                        img[y:y+2, x:x+2] = 255  # Diagonal

            elif label == 8:
                # Draw "8" - two circles stacked
                # Upper circle
                y, x = np.ogrid[:28, :28]
                mask_up = ((x - 14)**2 / 25) + ((y - 10)**2 / 25) <= 1
                img[mask_up] = 255
                mask_up_inner = ((x - 14)**2 / 16) + ((y - 10)**2 / 16) <= 1
                img[mask_up_inner] = 0
                # Lower circle
                mask_low = ((x - 14)**2 / 36) + ((y - 18)**2 / 36) <= 1
                img[mask_low] = 255
                mask_low_inner = ((x - 14)**2 / 20) + ((y - 18)**2 / 20) <= 1
                img[mask_low_inner] = 0

            elif label == 9:
                # Draw "9" - circle with tail
                y, x = np.ogrid[:28, :28]
                mask = ((x - 14)**2 + (y - 11)**2) <= 49
                img[mask] = 255
                mask_inner = ((x - 14)**2 + (y - 11)**2) <= 25
                img[mask_inner] = 0
                img[14:24, 16:20] = 255  # Tail down

            images.append(img)
            labels.append(label)

        return np.array(images), np.array(labels)

    def reset_game(self):
        """Reset game-specific state."""
        self.active_images = []
        self.score = 0
        self.next_spawn_time = self.spawn_interval
        self.image_counter = 0
        self.correct_identifications = 0
        self.incorrect_identifications = 0

    def _spawn_image(self):
        """Spawn a new random image from dataset."""
        if len(self.active_images) >= self.max_images:
            return

        if self.dataset_images is None or len(self.dataset_images) == 0:
            return

        screen_width, screen_height = self.config.screen_dimensions
        margin = 100

        # Random position
        position = np.array([
            np.random.uniform(margin, screen_width - margin),
            np.random.uniform(margin, screen_height - margin)
        ])

        # Random image from dataset
        idx = random.randint(0, len(self.dataset_images) - 1)
        image = self.dataset_images[idx]
        label = self.dataset_labels[idx]

        # Create image data
        image_id = f"image_{self.image_counter:03d}"
        self.image_counter += 1

        image_data = ImageData(
            image=image,
            label=label,
            position=position,
            display_size=self.image_display_size,
            spawn_time=self.current_time,
            duration=self.image_duration,
            image_id=image_id
        )

        self.active_images.append(image_data)

        # Log spawn event
        if self.logger:
            self.logger.log_event(
                self.current_step,
                self.current_time,
                "image_spawned",
                image_data.to_dict()
            )

    def _remove_expired_images(self):
        """Remove images that have expired."""
        expired_images = [img for img in self.active_images if img.is_expired(self.current_time)]

        for image_data in expired_images:
            self.active_images.remove(image_data)

            # Log expiration
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "image_expired",
                    {
                        "image_id": image_data.image_id,
                        "was_identified": image_data.identified
                    }
                )

    def get_game_state(self) -> GameState:
        """Build GameState with images and frame."""
        state = super().get_game_state()

        # Add image information
        state.active_images = self.active_images.copy()
        state.current_score = self.score

        # Add screen frame for ML processing
        state.screen_frame = self._capture_frame()

        return state

    def _capture_frame(self) -> Optional[np.ndarray]:
        """Capture current screen frame as numpy array.

        Returns:
            Frame as (H, W, 3) numpy array in RGB format, or None if headless
        """
        if self.headless or self.screen is None:
            return None

        import pygame

        # Get pixel array from pygame surface
        frame = pygame.surfarray.array3d(self.screen)

        # Transpose to (H, W, 3)
        frame = np.transpose(frame, (1, 0, 2))

        return frame

    def update_game_logic(self):
        """Update image spawning and expiration."""
        # Spawn new images if needed
        if self.current_time >= self.next_spawn_time:
            self._spawn_image()
            self.next_spawn_time = self.current_time + self.spawn_interval

        # Remove expired images
        self._remove_expired_images()

    def identify_image(self, image_id: str, predicted_label: int) -> bool:
        """Report an image identification.

        This method should be called by the controller when it identifies an image.

        Args:
            image_id: ID of the image being identified
            predicted_label: Predicted class/label

        Returns:
            True if identification was correct and points awarded
        """
        # Find the image
        image_data = None
        for img in self.active_images:
            if img.image_id == image_id:
                image_data = img
                break

        if image_data is None or image_data.identified:
            return False

        # Check if identification is correct
        is_correct = (predicted_label == image_data.label)

        if is_correct:
            # Award points
            self.score += self.points_per_correct
            self.correct_identifications += 1
            image_data.identified = True

            # Log correct identification
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "correct_identification",
                    {
                        "image_id": image_id,
                        "true_label": int(image_data.label),
                        "predicted_label": int(predicted_label),
                        "points_awarded": self.points_per_correct,
                        "new_score": self.score
                    }
                )

            return True
        else:
            # Log incorrect identification
            self.incorrect_identifications += 1

            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "incorrect_identification",
                    {
                        "image_id": image_id,
                        "true_label": int(image_data.label),
                        "predicted_label": int(predicted_label)
                    }
                )

            return False

    def _get_telemetry_data(self):
        """Add score and image count to telemetry."""
        data = super()._get_telemetry_data()

        data['score'] = self.score
        data['active_images'] = len(self.active_images)

        return data

    def render_game_elements(self):
        """Render dataset images."""
        if self.headless:
            return

        import pygame
        import cv2

        # Render images
        for image_data in self.active_images:
            # Get time remaining for fade effect
            time_remaining = image_data.time_remaining(self.current_time)
            fade_threshold = 1.0

            # Calculate alpha for fading
            if time_remaining < fade_threshold:
                alpha_factor = max(0.3, time_remaining / fade_threshold)
            else:
                alpha_factor = 1.0

            # Prepare image for display
            img = image_data.image

            # Convert grayscale to RGB if needed
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

            # Resize to display size
            img_resized = cv2.resize(img, image_data.display_size, interpolation=cv2.INTER_NEAREST)

            # Apply fade
            if alpha_factor < 1.0:
                img_resized = (img_resized * alpha_factor).astype(np.uint8)

            # Convert to pygame surface
            img_surface = pygame.surfarray.make_surface(
                np.transpose(img_resized, (1, 0, 2))
            )

            # Calculate position (centered)
            x = int(image_data.position[0] - image_data.display_size[0] / 2)
            y = int(image_data.position[1] - image_data.display_size[1] / 2)

            # Draw image
            self.screen.blit(img_surface, (x, y))

            # Draw border
            color = (0, 255, 0) if image_data.identified else (255, 255, 255)
            rect = pygame.Rect(x, y, image_data.display_size[0], image_data.display_size[1])
            pygame.draw.rect(self.screen, color, rect, 2)

            # Draw label if identified
            if image_data.identified:
                font = pygame.font.Font(None, 20)
                label_text = f"Label: {image_data.label}"
                surface = font.render(label_text, True, (0, 255, 0))
                self.screen.blit(surface, (x, y - 20))

        # Display score and stats
        font = pygame.font.Font(None, 36)
        score_text = f"Score: {self.score}"
        surface = font.render(score_text, True, (255, 255, 0))
        self.screen.blit(surface, (10, self.config.screen_dimensions[1] - 90))

        # Display accuracy
        font_small = pygame.font.Font(None, 24)
        total_attempts = self.correct_identifications + self.incorrect_identifications
        if total_attempts > 0:
            accuracy = (self.correct_identifications / total_attempts) * 100
            acc_text = f"Accuracy: {accuracy:.1f}% ({self.correct_identifications}/{total_attempts})"
        else:
            acc_text = f"Accuracy: N/A"

        surface = font_small.render(acc_text, True, (255, 255, 255))
        self.screen.blit(surface, (10, self.config.screen_dimensions[1] - 60))

        # Display active images count
        images_text = f"Active Images: {len(self.active_images)}"
        surface = font_small.render(images_text, True, (255, 255, 255))
        self.screen.blit(surface, (10, self.config.screen_dimensions[1] - 30))

    def check_game_termination(self) -> bool:
        """Terminate when episode duration reached."""
        return super().check_game_termination()

    def log_episode_start(self):
        """Log episode start."""
        if not self.logger:
            return

        self.logger.log_event(
            self.current_step,
            self.current_time,
            "episode_start",
            {
                "spawn_position": self.vehicle.position.tolist(),
                "spawn_orientation": float(self.vehicle.orientation),
                "episode_duration": self.episode_duration,
                "dataset": self.dataset_name,
                "max_images": self.max_images,
                "image_duration": self.image_duration
            }
        )

    def log_episode_end(self):
        """Log episode end with score and accuracy."""
        if not self.logger:
            return

        total_attempts = self.correct_identifications + self.incorrect_identifications
        accuracy = (self.correct_identifications / total_attempts * 100) if total_attempts > 0 else 0.0

        summary = {
            "total_steps": self.current_step,
            "total_time": self.current_time,
            "final_score": self.score,
            "images_spawned": self.image_counter,
            "correct_identifications": self.correct_identifications,
            "incorrect_identifications": self.incorrect_identifications,
            "accuracy": accuracy,
            "final_speed": self.vehicle.get_speed()
        }

        self.logger.log_event(
            self.current_step,
            self.current_time,
            "episode_end",
            {
                "reason": "time_limit",
                **summary
            }
        )

        self.logger.set_summary(summary)
