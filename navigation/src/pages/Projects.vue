<template>
  <q-page style="background-color: white">
      <div class="bg-grey-4 text-center flex-center" style="height:200px;">
          <div class="flex-center text-center column no-wrap" style="padding:10px;">
              <h2>Projects</h2>
              <p class="text-grey-9">Create your projects here, open them to add a level or modify the bot loadouts.</p>
            </div>
      </div>
      <div class="q-pa-md q-gutter-md">
          <q-btn class="bg-primary text-white" label="+ New Project" @click="openCreateProject" />
          <q-btn class="bg-primary text-white" label="Import Project" />
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
import { Project, defaultProject, Manager } from '../store/models'
import { Component } from 'vue-property-decorator'
import { ManagerStore } from 'src/store/ManagerStoreModule'

@Component({
  components: { ProjectWidgetComponent, CreateProjectComponent }
})
export default class Projects extends Vue {
    projects: Project[] = <Project[]>[
      defaultProject
    ]

    manager: Manager | undefined

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

    openCreateProject () {
      ManagerStore.setCreateProjectOpened(true)
      // this.$store.commit('player/updateCreateProjectOpened', true)
    }
}

</script>
