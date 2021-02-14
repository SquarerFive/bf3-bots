/* eslint-disable camelcase */
import axios, { AxiosResponse } from 'axios'
import L, { GeoJSON, LatLng } from 'leaflet'
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
    name: string
    transform: LevelTransform // make interface
    project_id: number
    date_created: Date
    date_modified: Date

    level_id: number
    friendly_kit: SoldierKitCollection
    enemy_kit: SoldierKitCollection

    id : number,

    roads: GeoJSON.FeatureCollection[],
    structures: GeoJSON.FeatureCollection[]
}

export interface Levels {
  levels: Level[]
}

export interface Projects {
  projects: Project[]
}

export interface Vector {
  x: number
  y: number
  z: number
}

export interface LevelBuildSettings {
  level_name: string
  start: Vector
  end: Vector
  voxel_step_size: number
  voxel_size: number
  iterations_x : number
  iterations_y : number,
  elevation_based_scoring: boolean
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
  id: number
  name: string
  path: string
  asset_type: string
  asset_team : string,
  tags: string[],
  children: GameAsset[]
}

export interface SoldierKit {
  primary_weapon: GameAsset[]
  primary_attachments: GameAsset[]
  secondary_weapon: GameAsset[]
  secondary_attachments: GameAsset[]
  primary_gadget: GameAsset[]
  secondary_gadget: GameAsset[]
  melee: GameAsset[]

  collection_id : number
  collection_slot: number

  kit_asset: GameAsset
  // the first item from this array will be used for kit_asset
  kit_assets: GameAsset[]
  appearance: GameAsset[]
}

export interface SoldierKitCollection {
  assault: SoldierKit
  engineer: SoldierKit
  support: SoldierKit
  recon: SoldierKit

  faction: number
  project_id: number
  level_id: number

  id : number
}

export interface TreeNode {
  label: string
  icon: string
  type: string
  children: TreeNode[],
  selectable: boolean | undefined,
  handler: CallableFunction | undefined,
  expandable: boolean,
  owner_id : number,
  id : number
}

export interface Transform {
  left: Vector,
  up: Vector,
  forward: Vector,
  trans: Vector
}

export interface Player {
  id : number,
  player_id : number,
  online_id : number,
  alive : boolean,
  is_squad_leader : boolean,
  is_squad_private : boolean,
  transform : Transform,
  in_vehicle: boolean,
  has_soldier: boolean,
  team: number,
  squad: number,
  health: number,
  is_human : boolean // artificial field
}

export const defaultGameAsset: GameAsset = {
  id: 0,
  name: 'default game asset',
  path: 'path to asset',
  asset_type: 'weapon_primary',
  asset_team: 'US',
  tags: [],
  children: []
}

export const defaultGameAsset_second: GameAsset = {
  id: 2,
  name: 'default game asset second',
  path: 'path to asset',
  asset_type: 'weapon_primary',
  asset_team: 'US',
  tags: [],
  children: []
}

export const defaultSoldierKit: SoldierKit = {
  primary_weapon: [],
  primary_attachments: [],
  secondary_weapon: [],
  secondary_attachments: [],
  primary_gadget: [],
  secondary_gadget: [],
  melee: [],
  collection_id: 0,
  collection_slot: 0,
  kit_asset: defaultGameAsset,
  appearance: [defaultGameAsset],
  kit_assets: [defaultGameAsset]
}

export const defaultSoldierKitCollection: SoldierKitCollection = {
  assault: defaultSoldierKit,
  engineer: defaultSoldierKit,
  support: defaultSoldierKit,
  recon: defaultSoldierKit,
  faction: 0,
  level_id: 0,
  project_id: 0,
  id: 0
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
  level_id: 0,
  friendly_kit: defaultSoldierKitCollection,
  enemy_kit: defaultSoldierKitCollection,
  id: 0,
  roads: [],
  structures: []
}

export class Manager {
  instance: Vue;
  api_url: string;
  currentPosition : Vector = { x: 0, y: 0, z: 0 };
  currentFBLevelName = '';
  currentAssetSelection : GameAsset[] = []
  shouldShowGameSettings = false
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
      if (e.friendly_kit == null) {
        e.friendly_kit = <SoldierKitCollection>deepCopy<SoldierKitCollection>(defaultSoldierKitCollection)
      }
      if (e.enemy_kit == null) {
        e.enemy_kit = <SoldierKitCollection>deepCopy<SoldierKitCollection>(defaultSoldierKitCollection)
      }
      e.friendly_kit.assault.kit_assets = [e.friendly_kit.assault.kit_asset ? e.friendly_kit.assault.kit_asset : defaultGameAsset]
      e.friendly_kit.engineer.kit_assets = [e.friendly_kit.engineer.kit_asset ? e.friendly_kit.engineer.kit_asset : defaultGameAsset]
      e.friendly_kit.support.kit_assets = [e.friendly_kit.support.kit_asset ? e.friendly_kit.support.kit_asset : defaultGameAsset]
      e.friendly_kit.recon.kit_assets = [e.friendly_kit.recon.kit_asset ? e.friendly_kit.recon.kit_asset : defaultGameAsset]
      e.enemy_kit.assault.kit_assets = [e.enemy_kit.assault.kit_asset ? e.enemy_kit.assault.kit_asset : defaultGameAsset]
      e.enemy_kit.engineer.kit_assets = [e.enemy_kit.engineer.kit_asset ? e.enemy_kit.engineer.kit_asset : defaultGameAsset]
      e.enemy_kit.support.kit_assets = [e.enemy_kit.support.kit_asset ? e.enemy_kit.support.kit_asset : defaultGameAsset]
      e.enemy_kit.recon.kit_assets = [e.enemy_kit.recon.kit_asset ? e.enemy_kit.recon.kit_asset : defaultGameAsset]
    })
    // levels[1].enemy_kit.level_id = 100
    console.log('get levels')
    console.log(defaultSoldierKitCollection)
    ManagerStore.setAvailableLevels(levels)
    return levels
  }

  async get_level (project_id : string, level_id: string): Promise<Level> {
    const response = await this.get(`/v1/project/${project_id}/level/${level_id}/`)
    const data : unknown = response.data
    console.log('get-level: ', response)
    const level : Level = <Level>data
    level.date_created = new Date(level.date_created)
    level.date_modified = new Date(level.date_modified)
    if (level.friendly_kit == null) {
      level.friendly_kit = <SoldierKitCollection>deepCopy<SoldierKitCollection>(defaultSoldierKitCollection)
    }
    if (level.enemy_kit == null) {
      level.enemy_kit = <SoldierKitCollection>deepCopy<SoldierKitCollection>(defaultSoldierKitCollection)
    }
    this.projectFeatureCollectionToGrid(level.roads, level)
    level.friendly_kit.assault.kit_assets = [level.friendly_kit.assault.kit_asset ? level.friendly_kit.assault.kit_asset : defaultGameAsset]
    level.friendly_kit.engineer.kit_assets = [level.friendly_kit.engineer.kit_asset ? level.friendly_kit.engineer.kit_asset : defaultGameAsset]
    level.friendly_kit.support.kit_assets = [level.friendly_kit.support.kit_asset ? level.friendly_kit.support.kit_asset : defaultGameAsset]
    level.friendly_kit.recon.kit_assets = [level.friendly_kit.recon.kit_asset ? level.friendly_kit.recon.kit_asset : defaultGameAsset]
    level.enemy_kit.assault.kit_assets = [level.enemy_kit.assault.kit_asset ? level.enemy_kit.assault.kit_asset : defaultGameAsset]
    level.enemy_kit.engineer.kit_assets = [level.enemy_kit.engineer.kit_asset ? level.enemy_kit.engineer.kit_asset : defaultGameAsset]
    level.enemy_kit.support.kit_assets = [level.enemy_kit.support.kit_asset ? level.enemy_kit.support.kit_asset : defaultGameAsset]
    level.enemy_kit.recon.kit_assets = [level.enemy_kit.recon.kit_asset ? level.enemy_kit.recon.kit_asset : defaultGameAsset]
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

  projectToGrid (position : Vector, level : Level) {
    const newX = this.remapValueRange(position.x, level.transform.min_point[0], level.transform.max_point[0], 0, level.transform.width)
    const newY = this.remapValueRange(position.z, level.transform.min_point[1], level.transform.max_point[1], 0, level.transform.height)

    return [newX, newY]
  }

  importFeatureCollectionJSON (featureCollections : GeoJSON.FeatureCollection[], level : Level) {
    const layers : L.Layer[][] = []
    if (featureCollections && Array.isArray(featureCollections)) {
      featureCollections.forEach(featureCollection => {
        layers.push([])
        featureCollection.features.forEach(feature => {
          if (feature !== undefined) {
            layers[layers.length - 1].push(GeoJSON.geometryToLayer(feature))
          }
        })
      })
    }
    return layers
  }

  projectFeatureCollectionToGrid (featureCollections : GeoJSON.FeatureCollection[], level : Level) {
    // console.log('featureCollection', featureCollections[0].features[0].geometry)
    const layers : L.Layer[][] = []
    if (featureCollections && Array.isArray(featureCollections)) {
      featureCollections.forEach(featureCollection => {
        layers.push([])
        featureCollection.features.forEach(feature => {
          // eslint-disable-next-line @typescript-eslint/no-unused-vars, no-unused-vars
          if (feature !== undefined) {
            const layerType = feature.geometry.type
            let projectedLayer : L.Layer|undefined
            const layer = GeoJSON.geometryToLayer(feature)
            if (layerType === 'Polygon') {
              const lp = <L.Polygon>layer
              const lpc : L.Polygon = new L.Polygon(lp.getLatLngs(), lp.options)
              const points = lpc.getLatLngs()
              // let projectedPoints : LatLng[] | LatLng[][] | LatLng[][][] = points
              // projectedPoints = []
              // let i = 0
              if (Array.isArray(points[0])) {
                if (Array.isArray(points[0][0])) {
                  const pt : LatLng[][][] = <LatLng[][][]>points
                  for (let i = 0; i < pt.length; ++i) {
                    for (let j = 0; j < pt[i].length; ++j) {
                      for (let k = 0; k < pt[i][j].length; ++k) {
                        if (this) {
                          const newPos = this.projectToGrid(
                            {
                              x: level.transform.height - pt[i][j][k].lat,
                              z: pt[i][j][k].lng,
                              y: 0
                            },
                            level
                          )
                          console.log('projecting', newPos)
                          pt[i][j][k] = new LatLng(newPos[0], newPos[1])
                        }
                      }
                    }
                  }
                } else {
                  const pt : LatLng[][] = <LatLng[][]>points
                  for (let i = 0; i < pt.length; ++i) {
                    for (let j = 0; j < pt[i].length; ++j) {
                      if (this) {
                        const newPos = this.projectToGrid(
                          {
                            x: (level.transform.height - pt[i][j].lat) - level.transform.height,
                            z: pt[i][j].lng,
                            y: 0
                          },
                          level
                        )
                        console.log('projecting', newPos)
                        pt[i][j] = new LatLng(newPos[0], newPos[1])
                      }
                    }
                  }
                }
              } else {
                const pt : LatLng[] = <LatLng[]>points
                for (let i = 0; i < pt.length; ++i) {
                  if (this) {
                    const newPos = this.projectToWorld(
                      pt[i].lng,
                      pt[i].lat,
                      level
                    )
                    pt[i] = new LatLng(newPos[0], newPos[1])
                  }
                }
                lpc.setLatLngs(pt)
                // e.layer = lp
              }
              projectedLayer = lpc
            } else if (layerType === 'Point') {
              const l : L.CircleMarker = <L.CircleMarker>layer
              const lc : L.CircleMarker = new L.CircleMarker(l.getLatLng(), l.options)
              lc.setRadius(1000)
              if (this) {
                const newPos = this.projectToWorld(
                  lc.getLatLng().lng,
                  lc.getLatLng().lat,
                  level
                )
                lc.setLatLng(new LatLng(newPos[0], newPos[1]))
                projectedLayer = lc
              }
            }
            if (projectedLayer) {
              layers[layers.length - 1].push(projectedLayer)
            }
          }
        })
      })
    }
    console.log('p Layers', layers, typeof layers[0])
    return layers
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

  async recalculateCosts (project_id : number, level_id : number, elevationBased : boolean, elevationAlphaPower : number, elevationAlphaBeta : number, elevationAlphaBetaPower : number) {
    const response = await this.post(`/v1/project/${project_id}/level/${level_id}/recalculate/`, {
      elevation_based_scoring: elevationBased,
      elevation_alpha_power: elevationAlphaPower,
      elevation_alpha_beta: elevationAlphaBeta,
      elevation_alpha_beta_power: elevationAlphaBetaPower
    })
    return response
  }

  async getGameAssets () {
    const response = await this.get('/v1/assets/')
    return response
  }

  async updateKits (project_id : string, level_id : string, friendly_kit_collection : SoldierKitCollection, enemy_kit_collection : SoldierKitCollection) {
    if (friendly_kit_collection.assault.kit_assets.length > 0) {
      friendly_kit_collection.assault.kit_asset = friendly_kit_collection.assault.kit_assets[0]
    }
    if (friendly_kit_collection.engineer.kit_assets.length > 0) {
      friendly_kit_collection.engineer.kit_asset = friendly_kit_collection.engineer.kit_assets[0]
    }
    if (friendly_kit_collection.support.kit_assets.length > 0) {
      friendly_kit_collection.support.kit_asset = friendly_kit_collection.support.kit_assets[0]
    }
    if (friendly_kit_collection.recon.kit_assets.length > 0) {
      friendly_kit_collection.recon.kit_asset = friendly_kit_collection.recon.kit_assets[0]
    }
    if (enemy_kit_collection.assault.kit_assets.length > 0) {
      enemy_kit_collection.assault.kit_asset = enemy_kit_collection.assault.kit_assets[0]
    }
    if (enemy_kit_collection.engineer.kit_assets.length > 0) {
      enemy_kit_collection.engineer.kit_asset = enemy_kit_collection.engineer.kit_assets[0]
    }
    if (enemy_kit_collection.support.kit_assets.length > 0) {
      enemy_kit_collection.support.kit_asset = enemy_kit_collection.support.kit_assets[0]
    }
    if (enemy_kit_collection.recon.kit_assets.length > 0) {
      enemy_kit_collection.recon.kit_asset = enemy_kit_collection.recon.kit_assets[0]
    }
    const response = await this.post(`/v1/project/${project_id}/level/${level_id}/kits/`, {
      friendly: friendly_kit_collection,
      enemy: enemy_kit_collection
    })
    return response
  }

  async exportProject (project_id : string) {
    const response = this.post(`/v1/project/${project_id}/export/`, {})
    return response
  }

  async getPlayers () : Promise<Player[]> {
    const response = await this.get('/v1/players/')
    return <Player[]>response.data
  }
}

/**
 * Deep copy function for TypeScript.
 * @param T Generic type of target/copied value.
 * @param target Target value to be copied.
 * @see Source project, ts-deepcopy https://github.com/ykdr2017/ts-deepcopy
 * @see Code pen https://codepen.io/erikvullings/pen/ejyBYg
 */
// eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-explicit-any
export const deepCopy = <T>(target: T): T | any => {
  if (target === null) {
    return target
  }
  if (target instanceof Date) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-explicit-any
    return new Date(target.getTime()) as any
  }
  if (target instanceof Array) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cp = [] as any[];
    // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-explicit-any
    (target as any[]).forEach((v) => { cp.push(v) })
    // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-explicit-any
    return cp.map((n: any) => deepCopy<any>(n)) as any
  }
  if (typeof target === 'object' && target !== {}) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-explicit-any
    const cp = { ...(target as { [key: string]: any }) } as { [key: string]: any }
    Object.keys(cp).forEach(k => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-explicit-any
      cp[k] = deepCopy<any>(cp[k])
    })
    return cp as T
  }
  return target
}
