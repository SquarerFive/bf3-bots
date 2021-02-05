<template>
  <q-layout view="hHh lpR fFf">

    <q-header bordered class="bg-grey-10 text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="left = !left" />

        <q-toolbar-title>
          {{
              currentProject.name
          }}
        </q-toolbar-title>

        <div class="row" style="padding: 5px;padding-left:8px;padding-right: 8px; border-style: solid; border-width: 1px; border-radius:2px; background-color: #262626; border-color: #595959">
          <q-btn @click="onClickTasks" label="tasks" color="warning" text-color="dark"/>
          <div style='padding-top: 8px;'>
            <q-linear-progress color="red" class="tasks_r" size="1px" dark stripe rounded :value="0.0" style="width:100px; "  />
          </div>
        </div>

      </q-toolbar>
    </q-header>

    <q-drawer dark show-if-above v-model="left" side="left" bordered class="bg-grey-10">
      <!-- drawer content -->
      <q-list dark class="">
        <q-item
          clickable
          v-ripple
          to='/projects/'
          >
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>Projects</q-item-section>
        </q-item>
        <q-item
            clickable
            v-ripple
            :to="`/project/${currentProject.project_id}/dashboard/`"
          >
            <q-item-section avatar>
              <q-icon name="dashboard" />
            </q-item-section>
            <q-item-section> Project Dashboard </q-item-section>
          </q-item>
      </q-list>
    </q-drawer>

    <q-dialog v-model="tasksOpened">
      <q-card style="width: 500px">
        <q-card-section>
          <div class="text-h6">Tasks</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-btn :disable="loading || tasks.length === 0" @click="onClickStartAllTasks" label="Start All Tasks" color="warning" text-color="dark" />
        </q-card-section>
        <q-list>
          <q-scroll-area style="height: 200px">
            <q-item v-for="task in tasks" :key="task.task_id">
              <q-item-section>
                <q-item-label>{{task.name}}</q-item-label>
                <q-item-label caption lines="2">Task ID: {{task.task_id}} Project ID: {{task.project_id}} Level ID: {{task.level_id}}</q-item-label>
              </q-item-section>

              <q-item-section side top>
                <q-item-label caption>idle</q-item-label>
                <q-btn flat icon="play_arrow">
                </q-btn>
              </q-item-section>
            </q-item>
          </q-scroll-area>
        </q-list>

        <q-card-actions align="right">
          <q-btn flat label="OK" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-page-container>
      <router-view style="height: 100%;" />
    </q-page-container>

    <q-footer bordered class="bg-grey-10 text-white">
      <q-toolbar>
        <p style='margin-bottom: 0; font-size:12px;'>
          BF3 Navigation Project &nbsp; <span style="color: #888888 "> 0.0.1:21012021 </span> <br> SquarerFive
          </p>
        <q-toolbar-title>
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>

  </q-layout>
</template>

<script lang="ts">
import { ManagerStore } from 'src/store/ManagerStoreModule'
import Vue from 'vue'
import { Component } from 'vue-property-decorator'
import { defaultProject, Manager, Project, ProjectTask } from '../store/models'

@Component({
  components: {}
})
export default class ProjectLayout extends Vue {
    left= false;
    right=false;
    tasksOpened = false;
    manager: Manager|undefined;
    currentProject : Project = defaultProject;
    tasks : ProjectTask[] = [];
    loading = false

    mounted () {
      this.manager = new Manager(this)
      this.manager.get_project(this.$route.params.id).then(
        result => {
          if (this.manager) {
            this.manager.currentProject = result
            this.currentProject = this.manager.currentProject
            console.log(result)
          }
        }
      ).catch(e => {
        console.log('Cannot get project ', e)
      })
    }

    onClickTasks () {
      if (this.manager) {
        this.loading = true
        this.tasksOpened = true
        this.tasks = []
        this.manager.getTasks(ManagerStore.currentProject.project_id).then(data => {
          console.log(data)
          this.tasks = data
          this.loading = false
        }).catch(e => {
          console.log(e)
          console.error(e)
          this.loading = false
        })
      }
    }

    onClickStartAllTasks () {
      if (this.manager) {
        this.manager.startAllTasks(ManagerStore.currentProject.project_id).then(result => {
          console.log('startAllTasks', result)
        }).catch(err => {
          console.error(err)
        })
      }
    }
}
</script>

<style lang="sass">
  .tasks_r
    border-radius: 0px 0px 2px 2px
    border-width: 0.5px
    border-color: #afafaf
    border-style: solid
    padding:17px
    margin-left: 5px
    padding-top: 8px
    padding-bottom:8px
</style>
