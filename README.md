# 423-Project
A fun game project named - "Maverick"


FUNCTIONALITIES:

The gamer drives a plane with arrow keys and mouse clicks to change speed and avoid obstacles and get the rewards. To begin with, the health of the plane will be 100 HP. The idea is to survive, get points, and defeat adventure levels until the health is depleted. Here's how health decreases:
* Obstacle hits:  Obstacles occur on the plane path and should be avoided to avoid damages. Running into them decreases the health of the plane. Each collision costs 10 HP. But it does not ensure that the plane is in Power Mode and instead, it only decreases health by 5 HP.
* RAIN: When it is raining, health is consumed at 0.1 HP/frame (3 HP/second at approximately 30 FPS).
* FOG: When there is fog around the obstacles will be hard to see thus improving the chances of collisions and reducing plane health

Health equal to 0 terminates the game.

COLLECTIBLES:
The collectibles also add to the score of the player upon collection to enhance the overall score. They are placed in the air route and the player earns more points upon hitting. The more the collectibles collected, the greater the final score.

ADVENTURE LEVELS :
* Obstacle Run: Obstacle Run Level is the first adventure mode in which the plane is constantly moving forward and the player has enough time to pass through a field of obstacles, being sure not to bump into it and earn points and survive as long as possible.

* Rapid Reward: Rapid Rewards is a special adventure mode that is similar to obstacle run except that the plane is faster and the player gathers a lot of items in his way in order to more quickly generate his score and the obstacles are cleared in the meantime. The increased plane speed and rich number of collectibles is the special feature of Rapid Rewards that enables the player to gain points fast without any concerns about the obstacles.

There will be three modes:
* Power Mode: In Power Mode, the gamer can shoot weapons in the plane, breaking down the way. The plane loses 1 HP per 20 shots or 1 shot, thus it is necessary to use it strategically.

* Ghost Mode: When the plane is ruined by the rain, Ghost Mode becomes activated, and the plane cannot be hit by the rain, which means that the plane is not losing the health by 0.1 HP per frame during the rain. This gives the player the opportunity to concentrate on his/her collection and evade the traps without the fear of getting caught by the rain.

* Barrel Roll mode: Its a type of an invincible mode where the plane moves forward while rolling sideways. In this mode rain, obstacles does not effect the planes health. It is similar to ghost mode but it can be activated whether there is rain or not. Barrel roll automatically activates the ghost mode for invincibility.

POV:
* First person perspective: 
First person perspective mode is a camera perspective that puts the player's point of view directly in the cockpit allowing them to feel like they are looking through the sky through the pilot.

* Third Person Perspective: 
The game is third-person perspective where the camera is placed behind and above the plane where the player is able to see the plane, obstacles and collectibles as he or she navigates through the environment.

* MINI-MAP:
a minimap is shown on the top right side of the screen to see the obstacle positions and collectibles through a 200 x 200 sized minimap.It can be turned on and off.

GAME OVER:
The Game Over has been activated upon the health of the plane reaching zero and the flight is conclusively ended. When this occurs, it locks up all the controls of the player and the plane halts. A "GAME OVER" text will then be shown prominently at the screen, together with the final score of the player and the current playthrough is terminated.

KEYBOARD CONTROLS:
* Arrow Up: Tilt the plane upward (pitch up)
* Arrow Down: Tilt the plane downward (pitch down)
* Arrow Left: Move the plane left
* Arrow Right: Move the plane right
* 'U' and 'u': Move the camera up
* 'D' and 'd': Move the camera down
* 'L' and 'l': Move the camera left
* 'R' and 'r': Move the camera right
* 'S' and 's': To restart the game
* 'F' and 'f': To enable and disable first-person perspective mode
* 'P' and 'p': Toggle Power Mode (enables shooting)
* 'G' and 'g': Toggle Ghost Mode (only active during rain)
* Spacebar: Fire a weapon when Power Mode is ON
* 'B' : Barrel Roll mode
* 'm': minimap on/off

MOUSE CONTROLS:
* Left click: Increase speed
* Right click: Decrease speed








