# bf3-bots
AI mod for BF3, this is an attempt to recreate BF2-like bots.

This mod is currently in development, some features may not function as intended (such as project export).



## ✨ Released: [Version 0.0.4](https://github.com/SquarerFive/bf3-bots/releases/tag/0.0.4)

## ✨ Main: [Version 0.0.45dev](https://github.com/SquarerFive/bf3-bots/tree/main)

## ✨ Master Branch: Features
- AI Teamwork
    - Bots can provide each other ammo or health (when they are at a critical state).
- Conquest, Conquest Assault, TDM and Domination support. 
    - Rush, CTF will soon be supported
- Multi-layer navigation mesh.
- DFAstar++ (highly optimized solution), and AStar pathfinding. Falling back to the latter if distance fields are not generated.
- Multiple tools to determine navigable parts of the map (all of these can work together):
    - Automated score-based navmesh generation (fast).
    - Path recorder, where the player can record their movements which modify the bias value on the nav mesh.
    - Map Editor, draw vector features to determine what areas are navigable and what aren't. Fairly similiar logic to the path recorder.
    - Automated voxel DF based navmesh generation (slow, but generates a more precise mesh).
    - Automated voxel depth based navmesh generation (fast).
- Work in progress vehicle controller, quite simple logic to allow the bots to get in a vehicle and drive to an objective by smoothly following a path.
- Loadout and asset manager, you may define what weapons, gadgets, melee and appearance related items are available for each slot in each kit. These can also differ for each map.
- Custom spawn points
    - Spawn points can be added for each team which the bot spawner will attempt to use. Otherwise they are spawned randomly around an objective.
- Runtime bot configuration
    - Modify the accuracy and aim offset of the bots, where the changes will propagate instantly.
- Extensible framework [need to document]
    - The behaviour of the bots are separated into "orders" and "actions", the tasks can be assigned to each of the actions. 
- Variable response times
    - The interval where the paths and actions of the bots can be set by using the `--interval` parameter for `startcomputetask`.

## 🖥 Requirements
- Battlefield 3 and Venice Unleashed

## ⛏ Installation
NOTICE: These binaries will be available on the 0.0.4 release. **(currently version is 0.0.4alpha2)**

0. You will need to open up two instances of CMD/Powershell for this.
1. Start the AI Server ```./dist/AIHelper/AIHelper.exe runserver --noreload```
2. Start the AI compute background task: ```./dist/AIHelper/AIHelper.exe startcomputetask```
3. Copy the directory 'bf3_bots_mod' into your BF3 server mods folder (ie, `MyServerInstance/Admin/Mods/`), then add `bf3_bots_mod` to your ModList.txt file.
4. Start your VU/BF3 server, hold down F1 in-game to focus on the UI. Create an account by registering (this is to prevent random players from messing with the settings).
5. On the top-left of the screen, open the menu and click 'Set Active' on the BF3 Bots Mod 0.0.4 project.
6. The wiki is frequently updated, please read through it if you are unsure on the setup process.

## 🖥 System Requirements
- CPU: Intel/AMD @3.5GHz - 4 cores 8 threads minimum
- RAM: 8GB RAM, nav-mesh on large maps are at-least 512MB
- HDD: 20GB Free
- Display: 1280x720. Lower resolutions may work but it's not supported.
- Typically most mid-range hardware after 2014 should be able to run the mod.


## UI
### Notes
It is recommended to use a resolution above 1280x720.
### 🛠 Contributing
- You will need NodeJS installed, then install yarn: `npm install yarn -g`
- Inside the navigation folder, run `yarn`
- Then to start it locally, run `quasar dev`
- Build it by running `quasar dev`, where the built site is located in /dist/spa/
- When compiling it with vuicc, you will need to point it to that folder.

