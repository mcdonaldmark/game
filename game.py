import arcade
import random
import os
import time

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Simple Arcade Game"
PLAYER_SPEED = 5
ENEMY_SPEED = 2
COIN_COUNT = 10
ENEMY_COUNT = 5
MAX_LEVEL = 5
ENEMY_DELAY = 3  # seconds before enemies can hit

# Asset paths
ASSETS_DIR = "assets"
PLAYER_SPRITE = os.path.join(ASSETS_DIR, "player.png")
COIN_SPRITE = os.path.join(ASSETS_DIR, "coin.png")
ENEMY_SPRITE = os.path.join(ASSETS_DIR, "enemy.png")
COIN_SOUND = os.path.join(ASSETS_DIR, "coin.mp3")
HIT_SOUND = os.path.join(ASSETS_DIR, "hit.mp3")


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_BLUE)

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Player sprite
        self.player = arcade.Sprite(PLAYER_SPRITE, 0.5)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player)

        # Load sounds
        self.coin_sound = arcade.load_sound(COIN_SOUND)
        self.hit_sound = arcade.load_sound(HIT_SOUND)

        # Score, level, and game state
        self.score = 0
        self.level = 1
        self.game_over = False
        self.show_congrats = False

        # Movement flags
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        # Level start time for enemy delay
        self.level_start_time = 0
        self.countdown_started = False  # Track if countdown has begun

        # Start first level
        self.setup_level()

    def setup_level(self):
        """Initialize coins and enemies for the current level."""
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Coins increase by 5 each level
        coins_this_level = COIN_COUNT + (self.level - 1) * 5
        for _ in range(coins_this_level):
            coin = arcade.Sprite(COIN_SPRITE, 0.3)
            coin.center_x = random.randint(20, SCREEN_WIDTH - 20)
            coin.center_y = random.randint(20, SCREEN_HEIGHT - 20)
            self.coin_list.append(coin)

        # Enemies increase by 2 per level
        enemies_this_level = ENEMY_COUNT + (self.level - 1) * 2
        for _ in range(enemies_this_level):
            enemy = arcade.Sprite(ENEMY_SPRITE, 0.4)
            enemy.center_x = random.randint(20, SCREEN_WIDTH - 20)
            enemy.center_y = random.randint(20, SCREEN_HEIGHT - 20)
            # Enemy speed increases each level
            speed = ENEMY_SPEED + (self.level - 1)
            enemy.change_x = random.choice([-speed, speed])
            enemy.change_y = random.choice([-speed, speed])
            self.enemy_list.append(enemy)

        # Reset player position
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2

        # Reset game state
        self.game_over = False
        self.show_congrats = False
        self.countdown_started = False
        self.level_start_time = 0  # Will start countdown on first key press

    def on_draw(self):
        self.clear()
        self.player_list.draw()
        self.coin_list.draw()
        self.enemy_list.draw()

        # Draw score
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 20)

        # Draw level
        arcade.draw_text(f"Level: {self.level}", SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30, arcade.color.WHITE, 20)

        # Draw countdown before enemies move
        if not self.game_over and self.countdown_started:
            elapsed = time.time() - self.level_start_time
            if elapsed < ENEMY_DELAY:
                remaining = ENEMY_DELAY - elapsed
                arcade.draw_text(
                    f"Get Ready! {int(remaining) + 1}",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2,
                    arcade.color.YELLOW,
                    30,
                    anchor_x="center"
                )

        # Draw game over or congratulations
        if self.game_over:
            message = "CONGRATULATIONS!" if self.show_congrats else "GAME OVER"
            arcade.draw_text(
                message,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                40,
                anchor_x="center"
            )
            arcade.draw_text(
                "Press ENTER to Start Over",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 50,
                arcade.color.WHITE,
                20,
                anchor_x="center"
            )

    def on_update(self, delta_time):
        if self.game_over:
            return

        # Only move player after countdown
        if self.countdown_started and time.time() - self.level_start_time >= ENEMY_DELAY:
            # Move player
            self.player.change_x = 0
            self.player.change_y = 0
            if self.up_pressed:
                self.player.change_y = PLAYER_SPEED
            if self.down_pressed:
                self.player.change_y = -PLAYER_SPEED
            if self.left_pressed:
                self.player.change_x = -PLAYER_SPEED
            if self.right_pressed:
                self.player.change_x = PLAYER_SPEED

            self.player_list.update()

            # Move enemies
            for enemy in self.enemy_list:
                enemy.center_x += enemy.change_x
                enemy.center_y += enemy.change_y
                # Bounce off edges
                if enemy.left < 0 or enemy.right > SCREEN_WIDTH:
                    enemy.change_x *= -1
                if enemy.bottom < 0 or enemy.top > SCREEN_HEIGHT:
                    enemy.change_y *= -1

            # Check coin collisions
            coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
            for coin in coins_hit:
                coin.remove_from_sprite_lists()
                self.score += 1
                arcade.play_sound(self.coin_sound)

            # Check enemy collisions
            enemies_hit = arcade.check_for_collision_with_list(self.player, self.enemy_list)
            if enemies_hit:
                arcade.play_sound(self.hit_sound)
                self.game_over = True
                self.show_congrats = False

            # Level complete
            if len(self.coin_list) == 0:
                if self.level >= MAX_LEVEL:
                    self.game_over = True
                    self.show_congrats = True
                else:
                    self.level += 1
                    self.setup_level()

    def on_key_press(self, key, modifiers):
        # Start countdown on first arrow key press
        if not self.countdown_started and key in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]:
            self.level_start_time = time.time()
            self.countdown_started = True

        # Restart if game over
        if self.game_over and key == arcade.key.ENTER:
            self.level = 1
            self.score = 0
            self.setup_level()
            return

        # Set movement flags (even during countdown)
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


def main():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()