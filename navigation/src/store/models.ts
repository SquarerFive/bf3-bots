/* eslint-disable camelcase */
import axios, { AxiosResponse } from 'axios'
import Vue from 'vue'
import { ManagerStore } from './ManagerStoreModule'

declare global {
  // eslint:disable-next-line
  interface Window { GameSyncManager : Manager }
  interface WebUI { Call: CallableFunction }
}

export interface Profile {
  username: string;
  token: string;
}

export interface Project {
  project_id: number;
  name: string;
  author: string | Profile;
  date_created: Date;
  date_modified: Date;
  description: string;
}

export interface LevelTransform {
    width: number;
    height: number;
    min_point: [number, number];
    max_point: [number, number];
}

export interface Level {
    name: string;
    transform: LevelTransform; // make interface
    project_id: number;
    date_created: Date;
    date_modified: Date;

    level_id: number;
}

export interface Levels {
  levels: Level[]
}

export interface Projects {
  projects: Project[]
}

export interface Vector {
  x: number,
  y: number,
  z: number
}

export interface LevelBuildSettings {
  level_name: string,
  start: Vector,
  end: Vector,
  voxel_step_size: number,
  voxel_size: number,
  iterations_x : number,
  iterations_y : number
}

export interface LevelBuildSyncPayload {
  build_settings: LevelBuildSettings,
  profile: Profile,
  project_id : number
}

export interface ProjectTaskData {
  x : number,
  y : number,
  elevation : number,
  values : number[]
}

export interface ProjectTask {
  name : string,
  data : ProjectTaskData[],
  project_id : number,
  level_id : number,
  task_id: number
}

export interface GameAsset {
  id: number,
  name: string,
  path: string,
  asset_type: string,
  asset_team : string
}

export interface SoldierKit {
  primary_weapon: GameAsset[],
  secondary_weapon: GameAsset[],
  primary_gadget: GameAsset[],
  secondary_gadget: GameAsset[],
  melee: GameAsset[]

  faction: number
}

export const defaultGameAsset: GameAsset = {
  id: 0,
  name: 'default game asset',
  path: 'path to asset',
  asset_type: 'weapon_primary',
  asset_team: 'US'
}

export const defaultSoldierKit: SoldierKit = {
  primary_weapon: [defaultGameAsset],
  secondary_weapon: [defaultGameAsset],
  primary_gadget: [defaultGameAsset],
  secondary_gadget: [defaultGameAsset],
  melee: [defaultGameAsset],
  faction: 0
}

export const defaultProfile: Profile = {
  username: '',
  token: ''
}

export const defaultProject: Project = {
  project_id: 0,
  name: 'default project',
  author: 'Admin',
  date_created: new Date(0),
  date_modified: new Date(9296292962),
  description: 'Hello World'
}

export const defaultLevel: Level = {
  name: 'default-level',
  transform: {
    width: 100,
    height: 100,
    min_point: [0, 0],
    max_point: [100, 100]
  },
  project_id: 0,
  date_created: new Date(0),
  date_modified: new Date(123456789),
  level_id: 0
}

export class Manager {
  instance: Vue;
  api_url: string;
  currentPosition : Vector = { x: 0, y: 0, z: 0 };
  currentFBLevelName = '';
  // build
  // buildProgress = 0.0

  constructor (instance: Vue) {
    this.instance = instance
    this.api_url = 'http://localhost:8000'
    this.attemptUseLocal()
    return this
  }

  get (url: string): Promise<AxiosResponse> {
    console.log('profile', ManagerStore.profile)
    return axios.get(this.api_url + url, {
      headers: {
        Authorization:
          'Token ' + ManagerStore.profile.token // (<State>this.instance.$store.state).manager.profile.token,
      }
    })
  }

  post (url: string, data: unknown, with_token = true): Promise<AxiosResponse> {
    console.log('profile: ', ManagerStore.profile)
    const headers = with_token ? {
      Authorization:
          'Token ' + ManagerStore.profile.token // (<State>this.instance.$store.state).manager.profile.token,
    } : {}
    return axios.post(this.api_url + url, data, {
      headers: headers
    })
  }

  async get_projects (): Promise<Project[]> {
    const response = await this.get('/v1/project/')
    const data : unknown = response.data
    console.log('Projects data', (<Projects>data).projects)
    const projects : Project[] = (<Projects>data).projects
    return projects
  }

  async get_project (project_id : string): Promise<Project> {
    const response = await this.get(`/v1/project/${project_id}/`)
    const data :unknown = response.data
    const project : Project = <Project>data
    return project
  }

  async get_levels (project_id: string): Promise<Level[]> {
    const response = await this.get(`/v1/project/${project_id}/level/`)
    const data : unknown = response.data
    // console.log("Level", data);
    const levels : Level[] = (<Levels>data).levels
    levels.forEach(e => {
      e.date_created = new Date(e.date_created)
      e.date_modified = new Date(e.date_modified)
    })
    return levels
  }

  async get_level (project_id : string, level_id: string): Promise<Level> {
    const response = await this.get(`/v1/project/${project_id}/level/${level_id}/`)
    const data : unknown = response.data
    const level : Level = <Level>data
    level.date_created = new Date(level.date_created)
    level.date_modified = new Date(level.date_modified)

    return level
  }

  get_level_base_cost_surface_uri (project_id : string, level_id : string, layer : number): string {
    return `${this.api_url}/v1/project/${project_id}/level/${level_id}/render/0/${layer}/`
  }

  get currentProject () : Project {
    // return this.instance.$store.getters['manager/getCurrentProject']
    // return (<State>this.instance.$store.state).manager.currentProject;
    return ManagerStore.currentProject
  }

  set currentProject (project : Project) {
    // this.instance.$store.commit('manager/updateCurrentProject', project)
    ManagerStore.setProject(project)
  }

  async login (username: string, password: string): Promise<Profile | null> {
    const response = await this.post('/v1/login/', {
      username: username,
      password: password
    }, false)
    if (response.status === 200) {
      const profile = <Profile>response.data
      // VU does not have localStorage available
      if (window.localStorage) {
        if (profile.username) { window.localStorage.setItem('username', profile.username) }
        if (profile.token) window.localStorage.setItem('token', profile.token)
      }
      // this.instance.$store.commit('manager/updateProfile', profile)
      ManagerStore.setProfile(profile)
      return profile
    }
    return null
  }

  attemptUseLocal () {
    const profile : Profile = defaultProfile
    // VU has no localStorage.
    if (window.localStorage) {
      profile.token = String(window.localStorage.getItem('token'))
      profile.username = String(window.localStorage.getItem('username'))

      if (profile.username !== '' && profile.token !== '' && profile.username !== 'null' && profile.token !== 'null') {
        // this.instance.$store.commit('manager/updateProfile', profile)
        ManagerStore.setProfile(profile)
        console.log('Logged in as ', profile)
      }
    }
  }

  updateCurrentPosition (x : number, y: number, z: number) {
    // console.log('update current pos', x, y, z)
    this.currentPosition = { x: x, y: y, z: z }
  }

  calculateBuildSettings (inBuildConfig : LevelBuildSettings) {
    const newConfig = inBuildConfig
    let maxPoint : Vector = { x: Math.ceil(newConfig.end.x), y: Math.ceil(newConfig.end.y), z: Math.ceil(newConfig.end.z) }
    const minPoint : Vector = { x: Math.ceil(newConfig.start.x), y: Math.ceil(newConfig.start.y), z: Math.ceil(newConfig.start.z) }
    newConfig.start = minPoint

    while ((maxPoint.x % newConfig.voxel_step_size) !== 0) {
      maxPoint = { x: maxPoint.x + 1, y: maxPoint.y, z: maxPoint.z }
    }
    while ((maxPoint.z % newConfig.voxel_step_size) !== 0) {
      maxPoint = { x: maxPoint.x, y: maxPoint.y, z: maxPoint.z + 1 }
    }
    newConfig.iterations_x = Math.ceil((maxPoint.x - newConfig.start.x) / newConfig.voxel_size)
    newConfig.iterations_y = Math.ceil((maxPoint.z - newConfig.start.z) / newConfig.voxel_size)
    newConfig.end = maxPoint
    newConfig.level_name = this.currentFBLevelName
    // this.buildProgress = 0.5
    return newConfig
  }

  updateBuildProgress (inBuildProgress : number) {
    // this.buildProgress = inBuildProgress
    ManagerStore.setLevelBuildProgress(inBuildProgress)
    // console.log('update build progress')
  }

  onFinishBuild () {
    const route = this.instance.$router.resolve({
      path: `/project/${ManagerStore.currentProject.project_id}/dashboard`
    })
    this.updateBuildProgress(0.0)
    location.href = route.href
  }

  updateCurrentLevelName (inLevelName : string) {
    this.currentFBLevelName = inLevelName
  }

  dispatchVext (eventName : string, args: unknown[]) {
    const stringArgs : string[] = []
    args.forEach(element => {
      stringArgs.push('\'' + String(element) + '\'')
    })
    console.log(stringArgs.join(', '))
    console.log(`WebUI.Call('DispatchEvent', '${eventName}', ${stringArgs.join(', ')} );`)
    // eslint-disable-next-line no-eval
    eval(`WebUI.Call('DispatchEvent', '${eventName}', ${stringArgs.join(', ')} );`)
  }

  callVext (eventName : string) {
    // eslint-disable-next-line no-eval
    eval(`WebUI.Call('${eventName}')`)
  }

  enableFocus () {
    this.callVext('EnableMouse')
    this.callVext('EnableKeyboard')
    this.callVext('BringToFront')
  }

  // focus back to the game

  resetFocus () {
    this.callVext('ResetMouse')
    this.callVext('ResetKeyboard')
  }

  remapValueRange (value : number, oldMin : number, oldMax : number, newMin : number, newMax : number) {
    const oldRange = (oldMax - oldMin)
    const newRange = (newMax - newMin)
    return (((value - oldMin) * newRange) / oldRange) + newMin
  }

  projectToWorld (x : number, y : number, level : Level) {
    y = level.transform.height - y
    console.log('reprojecting', x, y)
    const newX = this.remapValueRange(x, 0, level.transform.width, level.transform.min_point[0], level.transform.max_point[0])
    const newY = this.remapValueRange(y, 0, level.transform.height, level.transform.min_point[1], level.transform.max_point[1])
    console.log('new pos', newX, newY)
    return [newY, newX]
  }

  async getTasks (project_id : number) {
    const response = await this.get(`/v1/project/${project_id}/tasks/`)
    return <ProjectTask[]>response.data
  }

  async startAllTasks (project_id : number) {
    const response = await this.get(`/v1/project/${project_id}/tasks/start/`)
    return response
  }

  async updateLevelFeature (project_id : number, level_id : number, feature_type : string, data: unknown) {
    const response = await this.post(`/v1/project/${project_id}/level/${level_id}/add-feature/${feature_type}/`, data)
    return response
  }

  async resetLevel (project_id : number, level_id : number) {
    const response = await this.post(`/v1/project/${project_id}/level/${level_id}/reset/`, {})
    return response
  }

  async recalculateCosts (project_id : number, level_id : number) {
    const response = await this.get(`/v1/project/${project_id}/level/${level_id}/recalculate/`)
    return response
  }

  async getGameAssets () {
    const response = await this.get('/v1/assets/')
    return response
  }

  
}
