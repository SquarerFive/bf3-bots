<template>
    <q-card>
          <q-stepper
            v-model="step"
            ref="stepper"
            color="primary"
            animated
          >
            <q-step
              :name="1"
              title="Import Metadata"
              icon="settings"
              :done="step > 1"
            >
              <div class="row">
                <div class="col-6">
                    <q-input v-model="relativePath" outlined label="Relative Path to Project" hint="Example: models/Project/{ProjectName}/" />
                </div>
                <div class="col-1">
                    <q-separator vertical />
                </div>
              </div>
            </q-step>

            <q-step
              :name="2"
              title="Import Levels"
              caption="Optional"
              icon="create_new_folder"
              :done="step > 2"
            >
              <div class="row">
                <div class="col-6">
                    <q-input v-model="relativePath" outlined label="Relative Path to Project" hint="Example: models/Project/{ProjectName}/" />
                </div>
                <div class="col-1">
                    <q-separator vertical />
                </div>
                <div class="col-6">
                    test
                </div>
              </div>
            </q-step>

            <q-step
              :name="3"
              title="Review Data"
              icon="assignment"
            >
            </q-step>

            <q-step
              :name="4"
              title="Add Project"
              icon="add_comment"
            >

            </q-step>

            <template v-slot:navigation>
              <q-stepper-navigation>
                <q-btn @click="$refs.stepper.next()" color="primary" :label="step === 4 ? 'Finish' : 'Continue'" />
                <q-btn v-if="step > 1" flat color="primary" @click="$refs.stepper.previous()" label="Back" class="q-ml-sm" />
              </q-stepper-navigation>
            </template>
          </q-stepper>
    </q-card>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'

@Component({ components: { } })
export default class ImportProjectComponent extends Vue {
    step = 1
    relativePath = ''
}
</script>
