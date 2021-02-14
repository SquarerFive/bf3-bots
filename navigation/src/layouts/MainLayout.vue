<template>
  <q-layout view="lHr lpR lFr">
    <q-header
      bordered
      relveal
      class="bg-dark"
      style="font-size: 16px; max-height: 32px"
    >
      <q-toolbar style="font-size: 16px; max-height: 32px">
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          style="font-size: 12px; margin-top: -18px"
          :disable="!isLoggedIn"
          @click="drawerClick()"
        />

        <q-toolbar-title
          class="goldman"
          style="margin-top: -18px; font-size: 16px"
        >
        <q-icon name="api" size="20px" style="margin-right: 5px;"/>
          NAVIGATION MANAGER
        </q-toolbar-title>
        <q-toolbar-title
          class="text-left"
          style="font-size: 12px; margin-top: -18px"
        >
        </q-toolbar-title>
        <div class="row">
          <q-btn push dense  :disable="!isLoggedIn || currentProjectName === 'default project'" :color="spawnPointFaction === '0' ? 'blue' : 'red'" text-color="dark" :label="spawnPointFaction" style="font-size: 11px; margin-top: -18px; padding: 0px; margin-right: 0px; border-radius: 0" @click="onToggleSpawnPointFaction"/>
          <q-btn push dense :loading="isAddingSpawnPoint" :disable="!isLoggedIn || currentProjectName === 'default project'" :color="'warning'" text-color="dark" label="Add Spawn Point" style="font-size: 11px; margin-top: -18px; padding: 0px; margin-right: 5px; border-radius: 0" @click="onAddSpawnPoint"/>
        </div>
        <q-btn push dense :loading="isRecordingSaving" :disable="!isLoggedIn || currentProjectName === 'default project'" :color="isRecording ? 'red' : 'warning'" text-color="dark" label="Record" style="font-size: 11px; margin-top: -18px; padding: 0px; margin-right: 5px;" @click="onToggleRecording"/>
        <q-btn push dense :disable="!isLoggedIn" color="warning" text-color="dark" label="Show bot configuration" style="font-size: 11px; margin-top: -18px; padding: 0px; margin-right: 5px;" @click="toggleBotConfiguration"/>
        <q-btn push dense color="warning" text-color="dark" label="Switch input to game." style="font-size: 11px; margin-top: -18px; padding: 0px; margin-right: 5px;" @click="switchInputToGame"/>
        <p style="font-size: 11px" v-if="managerStore">
          Project: {{managerStore.currentProject.name}}
        </p>
        <q-btn
          flat
          label="LOGIN"
          class="bg-primary"
          style="font-size: 11px; margin-top: -18px; padding: 0px; margin-left: 5px"
          @click="openLogin()"
          v-if="!isLoggedIn"
        />
        <q-btn
          flat
          label="LOGOUT"
          class="bg-primary"
          style="font-size: 11px; margin-top: -18px; padding: 0px; margin-left: 5px"
          @click="onLogout()"
          v-if="isLoggedIn"
        />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" bordered content-class="bg-grey-1">
      <q-list>
        <q-item-label header class="text-grey-8"> Utilities </q-item-label>
        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
        <login-component />
      </q-list>
    </q-drawer>
    <login-component />
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import EssentialLink from 'components/EssentialLink.vue'
import LoginComponent from 'components/LoginComponent.vue'
import { ManagerStore, ManagerStoreModule } from '../store/ManagerStoreModule'

const linksData = [
  {
    title: 'Home',
    caption: 'Main page',
    icon: 'home',
    to: 'home',
    link: ''
  },
  {
    title: 'Projects',
    caption: 'Manage pathfinding projects',
    icon: 'map',
    to: 'projects',
    link: ''
  },
  {
    title: 'Github',
    caption: 'github.com/squarerfive',
    icon: 'code',
    link: 'https://github.com/squarerfive'
  }
]

import { Vue, Component } from 'vue-property-decorator'
import '../boot/windowGlobal'
import { Manager } from 'src/store/models'

@Component({
  components: { EssentialLink, LoginComponent }
})
export default class MainLayout extends Vue {
  leftDrawerOpen = false;
  essentialLinks = linksData;

  managerStore : ManagerStoreModule | null = null;
  isRecording = false
  spawnPointFaction = '0'
  isAddingSpawnPoint = false

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    // console.log(this.$store.getters['manager/getIsLoggedIn']);
    window.GameSyncManager = new Manager(this)
    this.managerStore = ManagerStore
  }

  drawerClick () {
    this.leftDrawerOpen = !this.leftDrawerOpen
    console.log('Drawer icon clicked')
  }

  switchInputToGame () {
    if (window.GameSyncManager) {
      window.GameSyncManager.resetFocus()
    }
  }

  toggleBotConfiguration () {
    ManagerStore.setShouldShowBotSettings(true)
  }

  get loginOpened () {
    // console.log("loginOpened", (<State>(this.$store.state).player.loginOpened));
    // return (<State>(this.$store.state)).player.loginOpened;
    return ManagerStore.loginOpened
  }

  set loginOpened (newValue: boolean) {
    // this.$store.commit('player/updateLoginOpened', newValue)
    ManagerStore.setLoginOpened(newValue)
  }

  openLogin () {
    this.loginOpened = true
    console.log('Login opened')
  }

  onLogout () {
    ManagerStore.setLoggedIn(false)
  }

  get playerPosition (): string {
    // tslint:disable-next-line
    // return String(this.$store.getters);
    return ''
  }

  get isLoggedIn () : boolean {
    return ManagerStore.loggedIn
    // return (<State>(this.$store.state)).manager.logged_in;
  }

  get currentProjectName () : string {
    if (ManagerStore) {
      console.log('GET PROJECT NAME', ManagerStore.currentProject.name)
      return ManagerStore.currentProject.name
    }
    return ''
  }

  recordingHandle : NodeJS.Timeout | null = null
  isRecordingSaving = false
  onToggleRecording () {
    if (this.isLoggedIn) {
      if (this.isRecording) {
        this.isRecording = false
        if (this.recordingHandle) {
          clearInterval(this.recordingHandle)
          this.recordingHandle = null
          this.isRecordingSaving = true
          window.GameSyncManager.finishRecordingPosition().then(() => { this.isRecordingSaving = false }).catch(err => { console.error(err); this.isRecordingSaving = false })
        }
      } else {
        this.isRecording = true
        this.recordingHandle = setInterval(() => {
          console.log('Hello World')
          window.GameSyncManager.updateRecordedPosition(window.GameSyncManager.currentPosition).catch(err => { console.error(err) })
        }, 500)
      }
    }
  }

  onToggleSpawnPointFaction () {
    if (this.spawnPointFaction === '0') {
      this.spawnPointFaction = '1'
    } else {
      this.spawnPointFaction = '0'
    }
  }

  onAddSpawnPoint () {
    this.isAddingSpawnPoint = true
    window.GameSyncManager.addSpawnPoint(window.GameSyncManager.currentPosition, parseInt(this.spawnPointFaction)).then(() => {
      this.isAddingSpawnPoint = false
    }).catch(err => {
      this.isAddingSpawnPoint = false
      console.error(err)
    })
  }
}
</script>
