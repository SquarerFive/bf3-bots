<template>
  <q-page style="background-color: white">
    <q-dialog full-width v-model="isOpenedImportProject">
      <import-project-component />
    </q-dialog>
      <div class="bg-grey-4 text-center flex-center" style="height:200px;">
          <div class="flex-center text-center column no-wrap" style="padding:10px;">
              <h2>Projects</h2>
              <p class="text-grey-9">Create your projects here, open them to add a level or modify the bot loadouts.</p>
            </div>
      </div>
      <div class="q-pa-md q-gutter-md">
          <q-btn push class="bg-primary col-1 text-white" label="New Project" @click="openCreateProject" icon="add_task" />
          <q-btn push class="bg-primary col-1 text-white" label="Import Project" @click="openImportProject" icon="file_upload" />
          <q-btn push class="bg-primary col-1 text-white" label="Refresh" :loading="isRefreshing" @click="refresh" icon="refresh" />
      </div>
    <div class="q-pa-md row items-start q-gutter-md">

      <div v-for="project in projects" :key="project.project_id">
          <project-widget-component :project="project"/>
        </div>
    </div>
    <create-project-component />
  </q-page>
</template>

<script lang="ts">
import Vue from 'vue'
import ProjectWidgetComponent from '../components/ProjectWidgetComponent.vue'
import CreateProjectComponent from '../components/CreateProjectComponent.vue'
import { Project, Manager } from '../store/models'
import { Component } from 'vue-property-decorator'
import { ManagerStore } from 'src/store/ManagerStoreModule'
import ImportProjectComponent from 'components/ImportProjectComponent.vue'

@Component({
  components: { ProjectWidgetComponent, CreateProjectComponent, ImportProjectComponent }
})
export default class Projects extends Vue {
    projects: Project[] = <Project[]>[]

    manager: Manager | undefined
    isOpenedImportProject = false
    isRefreshing = false

    mounted () {
      if (!this.manager) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
        this.manager = new Manager(this)
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
        this.manager.get_projects().then(p => {
          this.projects = p
        }).catch(e => {
          console.log('could not get projects for reason: ', e)
        })
        console.log(this.manager)
      }
    }

    refresh () {
      if (this.manager) {
        this.isRefreshing = true
        this.manager.get_projects().then(p => {
          this.projects = p
          this.isRefreshing = false
        }).catch(e => {
          console.log('could not get projects for reason: ', e)
          this.isRefreshing = false
          this.projects = []
        })
      }
    }

    openCreateProject () {
      ManagerStore.setCreateProjectOpened(true)
      // this.$store.commit('player/updateCreateProjectOpened', true)
    }

    openImportProject () {
      this.isOpenedImportProject = true
    }
}

</script>
