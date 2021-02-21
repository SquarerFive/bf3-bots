# bf3-bots
AI mod for BF3, this is an attempt to recreate BF2-like bots.

This mod is currently in development, some features may not function as intended (such as project export).



## ✨ Version 0.0.4a2 : Changelogs + Features
- Fixed: [#16](https://github.com/SquarerFive/bf3-bots/issues/16), [#15](https://github.com/SquarerFive/bf3-bots/issues/15), [#9](https://github.com/SquarerFive/bf3-bots/issues/9), and several bugs. Full Changelist:
```
Layered navmesh seemed to only be valid for layer 0.
Nav-mesh dimensions were inconrrect after adding a new level.
Improved the performance on AIServer by 12000%. Where it should now be in sync with the game.
Improved AI reaction times and moved compute tasks over to the startcomputetask command. Reaction times can be set using the --interval parameter.
Added the ability to set attachments for primary and secondary weapons on the bots.
Improved feedback within many UI elements, to let the user know whether a task is being run.
Bots now trace back if they are stuck on some object.
Exposed nav-mesh calculation parameters in the map editor.
AIServer is now distributable via an executable package.
Re-enabled vegetation.
Added filters to the asset browser.
Added csv tools to import and export dumped VEXT assets.
Database is now vacuumed after all tasks are deleted.
Create new arrays during the import if the nav-mesh on disk is corrupt.
Added bot driving interpolation, and vehicleController.
Added a level distance field mesh generator.
Added hybrid pathfinding (DFAstar++ for indoor maps).
Fixed invalid access to friendly/enemy kit collection on a new level.
Fixed custom spawner from attempting to generate an index with a range of 0.
Added elevation-based and DF-based generation options.
Added project JSON export.
Voxel-size now takes effect on the nav-mesh generation.
Level add-block now caches into memory rather than writing onto disk (causing the database to lock).
Added path-recorder.
Added custom spawner (for TDM).
Added EmitActionAsync.
Bots now supply each-other ammo or health if ammo/health is below a certain threshold.
Stop bots from attacking if the direct path (forward from the bot) is colliding with the distance field mesh. They will instead navigate around the obstructing object.
Built navmesh for Noshahr Canals TDM.
```
- Loadout manager, each slot contains all possible weapons - where one is randomly selected when the AI is spawned. Loadouts are set individually for each map and faction, for new maps a loadout can easily be cloned from an existing map or faction. Customize the attachments for each of the weapons.
![Loadout Screen](./docs/images/loadout_screen.png)
Asset manager, where you may add a weapon from the left into the selected list, this being all possible weapons the bot could spawn with.
![Asset Viewer](./docs/images/asset_viewer.png)
- AI Infantry Combat and Vehicle Driving
- Automated nav-mesh generation
![Add level prompt](./docs/images/add-level-0-0-4.png)
- WIP Interior/Subsurface Navigation
- Working server bullet damage


## ✨ Master Branch: Features
- Conquest, TDM and Domination support. 
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

