# bf3-bots
AI mod for BF3, reviving the Battlefield 2 experience

This mod is currently in early development. Feel free to contribute but there is no guaruntee that the mod will be stable if you plan on using it (I will only be providing support for those who wish to contribute at the moment).


## Version 0.0.35 : Changelogs
- AI Infantry Combat and Vehicle Driving
- Automated nav-mesh generation
- WIP Interior/Subsurface Navigation
- Working server bullet damage
- Loadout manager, each slot contains all possible weapons - where one is randomly selected when the AI is spawned. Loadouts are set individually for each map and faction, for new maps a loadout can easily be cloned from an existing map or faction.
- Fixed several bugs, the nav mesh now updates properly when a new map is loaded. Objectives are also cleared when this happens. 
- Basic bot accuracy modifiers, aiming offsets and randomization can be set during runtime.

## Requirements
- Anaconda 3 (https://www.anaconda.com/products/individual)
- Battlefield 3 and Venice Unleashed

## Installation
1. Install Anaconda 3
2. Open Powershell/CMD in the same folder where you have cloned bf3-bots. Example: `cd ~/repositories/bf3-bots/`
3. Run the following command `conda env create -f environment.yml`
4. Activate the conda environment: `conda activate battlefield`
5. CD into the AI server folder: `cd AIHelper`
6. Start the AI server: `python manage.py runserver`

## UI
### Notes
It is recommended to use a resolution above 1280x720.
### Contributing
- You will need NodeJS installed, then install yarn: `npm install yarn -g`
- Inside the navigation folder, run `yarn`
- Then to start it locally, run `quasar dev`
- Build it by running `quasar dev`, where the built site is located in /dist/spa/
- When compiling it with vuicc, you will need to point it to that folder.


## Features
- Flexible nav-mesh, it can be generated using a single command or use an existing one from the repo.
- Current support for up to 64 bots. (and this will increase as the mod becomes more optimized)
- AI Vehicle Interaction.
- Agnostic combat, AI see each other as normal players and will attack enemies regardless of whether they are human or bot.
- Conquest : AI attacks enemy objectives.
