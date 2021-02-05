<template>
  <q-dialog v-model="createProjectOpened" style="height: 55vh; width: 500px">
    <q-card style="height: 28vh; width: 500px">
      <q-card-section>
        <div class="text-h6">Create Project</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
          <q-input
            filled
            v-model="projectName"
            label="Project Name"
            hint="Name of your project"
            lazy-rules
            :rules="[
              (val) => (val && val.length > 0) || 'Please type something',
            ]"
          />

          <q-input
            filled
            v-model="projectDescription"
            label="Project Description"
            lazy-rules
          />
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Create"
          color="primary"
          v-close-popup
          @click="onSubmit"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { ManagerStore } from '../store/ManagerStoreModule'
// import { Profile } from '../store/models';

@Component
export default class CreateProjectComponent extends Vue {
  projectName = '';
  projectDescription = '';

  get createProjectOpened () {
    // console.log("loginOpened", (<State>(this.$store.state).player.loginOpened));
    return ManagerStore.createProjectOpened // (<State>this.$store.state).player.createProjectOpened;
  }

  set createProjectOpened (newValue: boolean) {
    // this.$store.commit('player/updateCreateProjectOpened', newValue);
    ManagerStore.setCreateProjectOpened(newValue)
  }

  onReset () {
    // todo
  }

  onSubmit () {
    this.$axios
      .post(
        'http://localhost:8000/v1/create-project/',
        {
          name: this.projectName,
          description: this.projectDescription
        },
        {
          headers: {
            Authorization: 'Token ' + ManagerStore.profile.token // String((<State>this.$store.state).manager.profile.token),
          }
        }
      )
      .then((resp) => {
        console.log(resp.data)
      })
      .catch((error) => {
        console.log(error)
      })
  }
}
</script>
