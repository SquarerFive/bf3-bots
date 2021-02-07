<template>
  <q-page class="bg-grey-10" style="color: white; height: 100%; width: 100%;margin-top:16px">
      <div class="q-pa-md q-gutter-md">
        <h5> Tools </h5>
        <div class="row items-start" v-if="loaded && managerStore != null">
          <tool-widget-component :toolName="'add level'" :to="`/project/${managerStore.currentProject.project_id}/tools/add-level`" style="margin-right:5px;"/>
          <!--
          <tool-widget-component :toolName="'loadout manager'" :to="`/project/${managerStore.currentProject.project_id}/tools/loadout-manager`" style="margin-right:5px;"/>
          -->
        </div>
      </div>
      <q-separator dark />
      <div class="q-pa-md q-gutter-md">
        <h5>Levels</h5>
        <div class="row items-start">
            <div v-for="level in levels" :key="level.name">
                <level-widget-component style="color: black; margin-right:5px;" :currentLevel="level" />
            </div>
        </div>
      </div>
  </q-page>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component } from 'vue-property-decorator'
import { defaultLevel, Level, Manager } from '../../store/models'
import LevelWidgetComponent from '../../components/LevelWidgetComponent.vue'
import ToolWidgetComponent from '../../components/ToolWidgetComponent.vue'
import { ManagerStore, ManagerStoreModule } from '../../store/ManagerStoreModule'

@Component(
  {
    components: { LevelWidgetComponent, ToolWidgetComponent }
  }
)
export default class ProjectDashboard extends Vue {
    manager: Manager|null = null;
    managerStore : ManagerStoreModule|undefined;
    loaded = false

    levels: Level[] = [defaultLevel];
    test () {
      console.log('hello')
      const routeInfo = this.$router.resolve({
        path: `/project/${ManagerStore.currentProject.project_id}/tools/add-level`
      })
      console.log('route', routeInfo.href)
      location.href = routeInfo.href
      // this.$router.push(`/project/${ManagerStore.currentProject.project_id}/tools/add-level`).then(e => {
      //   console.log('Route to :', e)
      // }).catch(err => {
      //   console.log('Failed to update router! ', err)
      // })
    }

    mounted () {
      this.manager = new Manager(this)
      this.manager.get_levels(this.$route.params.id).then(
        result => {
          console.log(result)
          this.levels = result
        }
      ).catch(e => {
        console.log('Failed to get levels. ', e)
        console.error('failed to get levels')
      })
      this.managerStore = ManagerStore
      this.loaded = true
      console.log('managerStore', this.managerStore)
    }
}
</script>
