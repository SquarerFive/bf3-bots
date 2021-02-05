<template>
  <q-card
    flat
    bordered
    class="my-card text-dark"
    style="min-width: 400px; max-width: 450px"
  >
    <q-card-section class="bg-grey-10 text-white">
      <div class="text-overline text-orange-5">{{project.author}}</div>
      <div class="text-h6">{{project.name}}</div>
    </q-card-section>

    <q-card-section
      class="bg-grey-2 text-small"
      style="padding-top: 10px; padding-bottom: 10px"
    >
      <div class="row">
        <div class="text-grey-8" style="padding: 0">
          <span style="font-size: 11px">Created</span
          ><span
            class="text-grey-6"
            style="float: right; margin-left: 15px; margin-right: 15px"
            >{{project.date_created}}</span
          >
        </div>
        <div class="text-grey-8" style="padding: 0">
          <span style="font-size: 11px">Modified</span
          ><span
            class="text-grey-6"
            style="float: right; margin-left: 15px; margin-right: 15px"
            >{{project.date_modified}}</span
          >
        </div>
        <div class="text-grey-8" style="padding: 0">
          <span style="font-size: 11px">Identifier</span
          ><span
            class="text-grey-6"
            style="float: right; margin-left: 15px; margin-right: 15px"
            >{{project.project_id}}</span
          >
        </div>
      </div>
    </q-card-section>

    <q-card-section class="text-grey-8">
      {{project.description}}
    </q-card-section>

    <q-separator dark />

    <q-card-actions>
      <q-btn flat :to="'/project/'+project.project_id+'/dashboard'">Open</q-btn>
      <q-btn flat @click="onProjectClicked">Set Active</q-btn>
      <q-btn flat>Inherit</q-btn>
    </q-card-actions>
  </q-card>
</template>

<script lang="ts">
import { ManagerStore } from 'src/store/ManagerStoreModule'
import { Vue, Component, Prop } from 'vue-property-decorator'
import { Project, Manager } from '../store/models'

@Component
export default class ProjectWidgetComponent extends Vue {
    manager : Manager | undefined;

    @Prop({ required: true }) readonly project!: Project;
    mounted () {
      this.manager = new Manager(this)
      console.log()
    }

    onProjectClicked () {
      if (this.manager) {
        console.log('onsetactiveproject')
        this.manager.dispatchVext('OnSetActiveProject', [JSON.stringify({ project_id: this.project.project_id, profile: ManagerStore.profile })])
      }
    }
}
</script>
