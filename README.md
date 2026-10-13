# Obstacle Course

**English** | [Русский](README.ru.md)

**Obstacle Course** is a third-person obstacle-course game developed with Unreal Engine 5.4.4. The player navigates an obstacle course through a canyon, dodges falling rocks, collects coins, rides moving platforms, and restores health at healing spheres. A deadly zone periodically damages the character while they remain inside it.

The project is implemented entirely in **Blueprint** using Unreal Engine 5.4.4. Gameplay logic and primary assets are located in `Content/ObstacleCourse/`.

> **Project status:** this version was created as a practical assignment. Some gameplay mechanics and run-completion flows are planned for future development. See [TODO](#todo).

## Table of Contents

- [Demo](#demo)
- [Requirements and Setup](#requirements-and-setup)
- [Maps and Gameplay Loop](#maps-and-gameplay-loop)
- [Controls](#controls)
- [Gameplay Mechanics](#gameplay-mechanics)
  - [Health and Death](#health-and-death)
  - [Coins](#coins)
  - [Healing](#healing)
  - [Falling Rocks](#falling-rocks)
  - [Deadly Zone](#deadly-zone)
  - [Moving Platforms](#moving-platforms)
  - [Environment and Prop Generation](#environment-and-prop-generation)
- [User Interface](#user-interface)
  - [Main Menu](#main-menu)
  - [HUD](#hud)
  - [Pause Menu](#pause-menu)
  - [Death Screen](#death-screen)
- [Project Architecture](#project-architecture)
- [Directory Structure](#directory-structure)
- [TODO](#todo)

## Demo

### Screenshots

#### Main Menu

![Main menu](Docs/Media/Screenshots/main_menu.png)

#### Gameplay

![Gameplay in the canyon](Docs/Media/Screenshots/canyon_gameplay.png)

#### Settings

![Game settings](Docs/Media/Screenshots/settings.png)

#### Pause Menu

![Pause menu](Docs/Media/Screenshots/pause_menu.png)

#### Death Zone

![Death screen](Docs/Media/Screenshots/death_zone.png)

### Video

Gameplay demo featuring movement through the canyon, obstacle interactions, coin collection, and healing spheres.

[Watch the gameplay demo](Docs/Media/Videos/gameplay_demo.webm)

## Requirements and Setup

### Requirements

- Unreal Engine **5.4.4**.
- The `obstacle_course.uproject` project file.
- The Python script used to generate environment props, if the props need to be regenerated.

### Launching the Project

1. Open `obstacle_course.uproject` in Unreal Engine 5.4.4.
2. Wait for the project and its assets to finish loading.
3. Open `Content/ObstacleCourse/Maps/LV_MainMenu`.
4. Press **Play** to start the game.

The main-menu map is `LV_MainMenu`.

The main gameplay level is `Content/ObstacleCourse/Maps/LV_Canyon`.

The editor Python script `Content/Python/generate_canyon.py` places environment props along the canyon spline. It is intended to distribute pine trees, boulders, and rocks along the route. Regeneration may be required if the spline geometry or its parameters change.

## Maps and Gameplay Loop

| Map | GameMode | Purpose |
| --- | --- | --- |
| `LV_MainMenu` | `BP_MainMenuGameMode` | Main menu, difficulty settings, and starting the game |
| `LV_Canyon` | `BP_ObstacleCourseGameMode` | Main gameplay |

### Gameplay Loop

1. The player launches the game and enters the main menu.
2. In Settings, the player can choose the damage dealt by falling rocks.
3. Selecting Start Game loads `LV_Canyon`.
4. During the run, the player collects coins, avoids obstacles, and restores health.
5. When the character dies, the death screen appears.
6. Pressing Escape during gameplay opens the pause menu.

Match settings are stored in `BP_ObstacleCourseGameInstance`. The `Rock Damage` parameter controls falling-rock damage and supports these values:

- `10` — low damage;
- `25` — medium damage;
- `50` — high damage.

The falling-rock spawner retrieves the current value through `GetRockDamage`.

## Controls

Player input is handled using Enhanced Input and the `IMC_ObstacleCourse` mapping context.

| Action | Input Action | Controls |
| --- | --- | --- |
| Character movement | `IA_ObstacleCourseMove` | WASD |
| Look | `IA_ObstacleCourseLook` | Mouse |
| Jump | `IA_ObstacleCourseJump` | Space |
| Pause | `IA_ObstacleCoursePauseMenu` | Escape |

### Character and Input Handling

The main character class is `BP_ObstacleCourseCharacter`. It uses a third-person camera and rotates the character body to match the movement direction.

`BP_ObstacleCoursePlayerController` handles movement and looking. Jump logic is implemented directly in the character class.

## Gameplay Mechanics

### Health and Death

The health system is implemented in `BP_HealthComponent`, which is attached to the character. The component is responsible for:

- storing current and maximum health (`Health` and `DefaultHealth`);
- handling damage through the `OnTakeAnyDamage` event;
- notifying listeners about damage through `OnOwnerDamaged`;
- notifying listeners about death through `OnOwnerDied`.

When a rock hits the player, the camera shakes using `CS_PlayerRockHit`.

When the character dies, ragdoll physics are enabled with `SetSimulatePhysics`. Character control is disabled, and the HUD displays `WBP_DeathScreen`.

### Coins

Coin collection is implemented in `BP_Coin`.

- The coin rotates in place.
- The **Magnetic Zone** pulls the coin toward the player.
- The **Pick Up Zone** triggers coin collection.
- Collecting a coin plays a squash animation, sound, and visual effects.
- The player's coin count is increased through `EarnPlayerCoins` in Player State.
- The coin actor is destroyed after collection.

Collected coins can be spent to restore health.

### Healing

Healing interactions use the `BPI_HealthHandler` Blueprint Interface and its `TryHealingByCoins` method. Healing costs coins; the cost is configured through the `Price` parameter.

`BP_HealingSphere` implements the healing sphere:

1. When the player enters the sphere, a timer starts periodic healing attempts.
2. If the healing conditions are met, the player restores health in exchange for coins.
3. Cross-shaped visual effects and a meditation sound play during healing.
4. When the player leaves the sphere, the latent object `BPW_DeactivateHealing` disables the corresponding effect.

### Falling Rocks

The falling-rock mechanic consists of three main Blueprint classes.

#### `BP_Rock`

A physics-driven rock that damages the player on collision. An impact sound and dust effect play when it hits.

#### `BP_FallingRock`

A warning area that provides visual and audio feedback before a rock falls. It:

- displays a VFX marker for the impact location;
- plays a falling sound;
- spawns a `BP_Rock` instance at an offset above the target location.

#### `BP_FallingRockSpawner`

The spawner activates automatically when the player comes within `Activation Distance`.

After activation, it periodically chooses a position ahead of or to the side of the player. Position selection uses:

- `Forward Distance Range`;
- `Right Distance Range`.

Before creating a new warning area, the spawner checks the minimum distance from previously used points. This reduces the likelihood of rocks appearing too close together.

Falling-rock damage is controlled by `Rock Damage`, stored in `BP_ObstacleCourseGameInstance`.

### Deadly Zone

`BP_DeathZone` defines an area that periodically damages the character while the player remains inside it. Damage is applied using a timer.

Additional effects include:

- a heartbeat sound;
- a red post-process effect that reinforces the sense of danger.

When the player leaves the zone, the timer and sound stop.

### Moving Platforms

`BP_MovingPlatform` implements platform movement, controlled by the `MoveCycle` Timeline.

Entering the platform trigger can temporarily increase the character's movement speed. The relevant parameters are:

- `Default Speed` — normal movement speed;
- `Boost Speed` — speed while boosted;
- `Boost Duration` — boost duration.

Colliding with the platform can also cause damage.

### Environment and Prop Generation

#### `BP_CanyonPath`

An actor containing the canyon route spline. A Python script uses the spline to place environment objects along the gameplay route. The actor itself contains almost no gameplay logic.

The generated props include pine trees, boulders, and rocks. Generation script: `Content/Python/generate_canyon.py`.

#### `BP_CustomizableSign`

A sign actor with configurable text, allowing signs with different messages to be placed in the game world.

## User Interface

The UI is built with UMG and Blueprint Widgets. Its visual style includes decorative panels, progress-bar masks, coin display elements, and the Bangers font.

Standard buttons use `WBP_RegularButton`, which supports hover and click sound effects.

### Main Menu

The main menu is implemented in `WBP_MainMenu`. The widget is created by `BP_MainMenuPlayerController`. The interface uses the UI Only input mode with the cursor enabled.

A `WidgetSwitcher` is used to switch between sections:

- **Start Game** — opens the gameplay map `LV_Canyon`.
- **Settings** — selects falling-rock damage.
- **Credits** — displays credits.
- **Quit** — exits the game.

Back buttons return to the main menu screen.

#### Settings

The Settings section contains `ComboBox_RockDamage`, labelled `Rock damage:`. Available values are `10`, `25`, and `50`.

The selected value is stored in `BP_ObstacleCourseGameInstance` and used by the falling-rock spawner. Dropdown rows are displayed through `WBP_ListRow`.

### HUD

The gameplay UI is implemented in `WBP_PlayerInterface` and created by `BP_ObstacleCourseHUD`. The HUD displays:

- **Health** — the character's current and maximum HP.
- **Coins** — the number of coins collected by the player.

UMG bindings are used to display the current state.

### Pause Menu

The pause menu is implemented in `WBP_PauseMenu`. When Escape is pressed, the controller pauses the game with `Set Game Paused`, enables the cursor, and displays the menu.

- **Resume** — closes the pause menu, unpauses the game, and restores Game Only input mode.
- **Main Menu** — opens `LV_MainMenu`.
- **Quit** — exits the game.

### Death Screen

The death screen is implemented in `WBP_DeathScreen`. `BP_ObstacleCourseHUD` subscribes to the character's `OnOwnerDied` event. On death, the gameplay HUD is hidden and the death screen is displayed.

In the current version, the death screen only communicates that the character has died. Restarting the run or returning to the main menu from this screen is planned for future development.

## Project Architecture

The main systems are separated by responsibility.

| System | Main classes | Responsibility |
| --- | --- | --- |
| Character | `BP_ObstacleCourseCharacter` | Movement and jumping |
| Input and control | `BP_ObstacleCoursePlayerController` | Input and player control |
| Game mode | `BP_MainMenuGameMode`, `BP_ObstacleCourseGameMode` | Game behavior for each map |
| Game state | `BP_ObstacleCourseGameState` | Gameplay state |
| Player state | `BP_ObstacleCoursePlayerState` | Player data, including coins |
| Game settings | `BP_ObstacleCourseGameInstance` | Settings preserved across map transitions |
| Health | `BP_HealthComponent`, `BPI_HealthHandler` | Damage, death, and healing interactions |
| Gameplay actors | `BP_Coin`, `BP_HealingSphere`, `BP_Rock` | Coins, healing, and rock interactions |
| Obstacles | `BP_FallingRock`, `BP_FallingRockSpawner`, `BP_DeathZone`, `BP_MovingPlatform` | Hazards and interactive level elements |
| UI | `WBP_MainMenu`, `WBP_PlayerInterface`, `WBP_PauseMenu`, `WBP_DeathScreen` | Main menu, HUD, pause menu, and death screen |
| Environment generation | `BP_CanyonPath`, `generate_canyon.py` | Route spline and prop placement |

## Directory Structure

The main Blueprint classes and assets are located in `Content/ObstacleCourse/`.

```text
Content/ObstacleCourse/
├── Characters/
│   └── BP_ObstacleCourseCharacter
├── Core/
│   ├── GameModes/
│   │   ├── BP_MainMenuGameMode
│   │   └── BP_ObstacleCourseGameMode
│   ├── GameStates/
│   │   └── BP_ObstacleCourseGameState
│   ├── GameInstances/
│   │   └── BP_ObstacleCourseGameInstance
│   ├── PlayerControllers/
│   │   ├── BP_MainMenuPlayerController
│   │   └── BP_ObstacleCoursePlayerController
│   ├── PlayerStates/
│   │   └── BP_ObstacleCoursePlayerState
│   ├── HUD/
│   │   └── BP_ObstacleCourseHUD
│   └── EnhancedInput/
│       ├── IMC_ObstacleCourse
│       └── IA_*
├── Blueprints/
│   ├── BP_HealthComponent
│   ├── BPI_HealthHandler
│   ├── BP_Coin
│   ├── BP_HealingSphere
│   ├── BP_Rock
│   ├── BP_FallingRock
│   ├── BP_FallingRockSpawner
│   ├── BP_DeathZone
│   ├── BP_MovingPlatform
│   ├── BP_CanyonPath
│   └── BP_CustomizableSign
├── UI/
│   ├── WBP_MainMenu
│   ├── WBP_PlayerInterface
│   ├── WBP_PauseMenu
│   └── WBP_DeathScreen
└── Maps/
    ├── LV_MainMenu
    └── LV_Canyon

Content/Python/
└── generate_canyon.py
```

## TODO

This version was created as a practical assignment. The following items describe planned improvements to gameplay and the user interface.

### Level

- [ ] Extend the gameplay route to the end of the canyon.
- [ ] Finish placing and tuning gameplay mechanics throughout the level.
- [ ] Add a finish area and successful-run completion logic.
- [ ] Implement a score calculation for each run.
- [ ] Add a level-completion screen showing the final result.

### Gameplay Loop

- [ ] Allow the player to restart a run from the death screen.
- [ ] Allow the player to return to the main menu from the death screen.
- [ ] Correctly reset game state when starting another run.
- [ ] Verify pause, death, and map-transition handling.

### UI and Feedback

- [ ] Display the final score on the run-completion screen.
- [ ] Add appropriate feedback when the level is completed successfully.
- [ ] Improve game settings and add presets.
- [ ] Ensure the UI is consistent across gameplay, pause, death, and run-completion states.

### Testing and Polish

- [ ] Verify that the selected difficulty is preserved across map transitions.
- [ ] Test interactions between coin collection, healing, and the health system.
- [ ] Test obstacle behavior across repeated runs.
- [ ] Perform a final end-to-end check from the main menu through run completion.

### Documentation

- [ ] Add up-to-date screenshots of the main menu, settings, and gameplay.
- [ ] Record a short gameplay walkthrough.
- [ ] Update the README after implementing the finish and restart flow.
