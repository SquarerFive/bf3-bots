<template>
    <q-card class="my-card" style="min-width: 300px;">
      <q-img src="https://static.wikia.nocookie.net/battlefield/images/d/db/Caspian-border-promo.jpg">
        <div class="absolute-bottom">
          <div class="text-h6">{{currentLevel.name}}</div>
          <div class="text-subtitle3">Level Instance</div>
        </div>
      </q-img>

      <q-card-actions>
        <q-btn flat :to="`/project/${currentLevel.project_id}/level/${currentLevel.level_id}`">Map Editor</q-btn>
        <q-btn flat>Edit</q-btn>
      </q-card-actions>
    </q-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Prop } from 'vue-property-decorator'
import { defaultLevel, Level } from '../store/models'

@Component
export default class LevelWidgetComponent extends Vue {
    @Prop({
      default: defaultLevel, required: true
    }) readonly currentLevel!: Level;
}

</script>
