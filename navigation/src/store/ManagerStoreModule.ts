import { storeInstance } from './index'
import { Action, getModule, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import { Level, Profile, Project, Transform } from './models'

@Module({
  dynamic: true,
  store: storeInstance,
  namespaced: true,
  name: 'ManagerStoreModule'
})
export class ManagerStoreModule extends VuexModule {
    loggedIn = false
    profile : Profile = {
      username: '',
      token: ''
    }

    currentProject : Project = {
      project_id: 0,
      name: 'default project',
      author: 'Admin',
      date_created: new Date(0),
      date_modified: new Date(9296292962),
      description: 'Hello World'
    }

    loginOpened = false
    createProjectOpened = false
    levelBuildProgress = 0.0

    availableLevels: Level[] = []
    shouldShowBotSettings = false

    currentPlayerTransform : Transform = {
      forward: { x: 0, y: 0, z: 0 },
      left: { x: 0, y: 0, z: 0 },
      up: { x: 0, y: 0, z: 0 },
      trans: { x: 0, y: 0, z: 0 }
    }

    @Mutation
    SET_LOGGEDIN (newLoggedIn: boolean) {
      this.loggedIn = newLoggedIn
    }

    @Action
    setLoggedIn (newLoggedIn: boolean) {
      this.SET_LOGGEDIN(newLoggedIn)
    }

    @Mutation
    SET_PROFILE (newProfile : Profile) {
      this.profile = newProfile
    }

    @Action
    setProfile (newProfile : Profile) {
      this.SET_PROFILE(newProfile)
      this.setLoggedIn(true)
    }

    @Mutation
    SET_PROJECT (newProject : Project) {
      this.currentProject = newProject
    }

    @Action
    setProject (newProject : Project) {
      this.SET_PROJECT(newProject)
    }

    @Mutation
    SET_LOGIN_OPENED (newLoginOpened: boolean) {
      this.loginOpened = newLoginOpened
    }

    @Action
    setLoginOpened (newLoginOpened : boolean) {
      this.SET_LOGIN_OPENED(newLoginOpened)
    }

    @Mutation
    SET_CREATE_PROJECT_OPENED (newProjectOpened : boolean) {
      this.createProjectOpened = newProjectOpened
    }

    @Action
    setCreateProjectOpened (newProjectOpened : boolean) {
      this.SET_CREATE_PROJECT_OPENED(newProjectOpened)
    }

    @Mutation
    SET_LEVEL_BUILD_PROGRESS (newProgress : number) {
      this.levelBuildProgress = newProgress
    }

    @Action
    setLevelBuildProgress (newProgress : number) {
      this.SET_LEVEL_BUILD_PROGRESS(newProgress)
    }

    @Mutation
    SET_AVAILABLE_LEVELS (newAvailableLevels : Level[]) {
      this.availableLevels = newAvailableLevels
    }

    @Action
    setAvailableLevels (newAvailableLevels : Level[]) {
      this.SET_AVAILABLE_LEVELS(newAvailableLevels)
    }

    @Mutation
    SET_SHOULD_SHOW_BOT_SETTINGS (newShouldShowBotSettings : boolean) {
      this.shouldShowBotSettings = newShouldShowBotSettings
    }

    @Action
    setShouldShowBotSettings (newShouldShowBotSettings : boolean) {
      this.SET_SHOULD_SHOW_BOT_SETTINGS(newShouldShowBotSettings)
    }

    @Mutation
    SET_CURRENT_PLAYER_TRANSFORM (newTransform : Transform) {
      this.currentPlayerTransform = newTransform
    }

    @Action
    setCurrentPlayerTransform (newTransform : Transform) {
      this.SET_CURRENT_PLAYER_TRANSFORM(newTransform)
    }
}

export const ManagerStore = getModule(ManagerStoreModule)
