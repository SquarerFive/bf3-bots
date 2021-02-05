<template>
  <q-layout view="hHh LpR fFf">

    <q-header elevated class="bg-dark text-white" height-hint="98">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="left = !left" />

        <q-toolbar-title class="goldman">
          SC Map
        </q-toolbar-title>

        <q-btn dense flat round icon="menu" @click="right = !right" />
      </q-toolbar>

      <q-tabs align="left">
        <q-route-tab to="#wake" label="Wake Island" />
        <q-route-tab to="#metro" label="Operation Metro" />
        <q-route-tab to="#oman" label="Gulf of Oman" />
      </q-tabs>
    </q-header>

    <q-drawer show-if-above v-model="left" side="left" bordered>
      <!-- drawer content -->
        <q-scroll-area class="fit">
            <q-list>
                <q-item-label header>Tools</q-item-label>
                <q-item tag="label" v-ripple>
                    <q-item-section avatar>
                        <q-icon name="edit" />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label>Edit</q-item-label>
                    </q-item-section>
                    <q-item-section side >
                        <q-toggle color="blue" v-model="enableEditing" val="enableEditing" />
                    </q-item-section>
                </q-item>
                <q-item v-ripple>
                    <q-item-section avatar>
                        <q-icon name="linear_scale" />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label>Polygon Tool</q-item-label>
                    </q-item-section>
                </q-item>
                <q-item v-ripple>
                    <q-item-section avatar>
                        <q-icon name="edit_road" />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label>Road Tool</q-item-label>
                    </q-item-section>
                </q-item>
            </q-list>
        </q-scroll-area>
    </q-drawer>

    <q-drawer show-if-above v-model="right" side="right" bordered>
      <!-- drawer content -->
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script>
export default {
  data () {
    return {
      left: false,
      right: false,
      enableEditing: false
    }
  }
}
</script>
