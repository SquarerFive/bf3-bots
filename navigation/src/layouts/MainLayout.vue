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
          @click="leftDrawerOpen = !leftDrawerOpen; drawerClick()"
        />

        <q-toolbar-title
          class="goldman"
          style="margin-top: -18px; font-size: 16px"
        >
          NAVIGATION MANAGER
        </q-toolbar-title>
        <q-toolbar-title
          class="text-left"
          style="font-size: 12px; margin-top: -18px"
        >
        </q-toolbar-title>
        <p style="font-size: 11px" v-if="managerStore">
          Project: {{managerStore.currentProject.name}}
        </p>
        <q-btn
          flat
          label="LOGIN"
          class="bg-primary"
          style="font-size: 11px; margin-top: -18px; padding: 0px"
          @click="openLogin()"
          v-if="!isLoggedIn"
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
    title: 'Github',
    caption: 'github.com/squarerfive',
    icon: 'code',
    link: 'https://github.com/squarerfive'
  },
  {
    title: 'Projects',
    caption: 'Manage pathfinding projects',
    icon: 'map',
    to: 'projects',
    link: ''
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

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    // console.log(this.$store.getters['manager/getIsLoggedIn']);
    window.GameSyncManager = new Manager(this)
    this.managerStore = ManagerStore
  }

  drawerClick () {
    console.log('Drawer icon clicked')
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

  get playerPosition (): string {
    // tslint:disable-next-line
    // return String(this.$store.getters);
    return ''
  }

  get isLoggedIn () : boolean {
    return ManagerStore.loggedIn
    // return (<State>(this.$store.state)).manager.logged_in;
  }
}
</script>
