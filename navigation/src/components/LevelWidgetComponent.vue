<template>
    <q-card class="my-card" style="min-width: 300px;">
      <q-img :src="findImageURLForLevel(currentLevel.name)">
        <div class="absolute-bottom">
          <div class="text-h6">{{currentLevel.name}}</div>
          <div class="text-subtitle3">Level Instance</div>
        </div>
      </q-img>

      <q-card-actions>
        <q-btn flat :to="`/project/${currentLevel.project_id}/level/${currentLevel.level_id}`">Map Editor</q-btn>
        <q-btn flat :to="`/project/${currentLevel.project_id}/level/${currentLevel.level_id}/loadout-manager`">Loadout Manager</q-btn>
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

    findImageURLForLevel (levelName : string) {
      const map = {
        'Levels/XP3_Valley/XP3_Valley': 'https://static.wikia.nocookie.net/battlefield/images/e/e4/AK_Death_Valley.png',
        'Levels/XP1_004/XP1_004': 'https://static.wikia.nocookie.net/battlefield/images/f/fd/WAKE_ISLAND_2014_BTK_OVERVIEW.png'
      }

      const found : [string, string] | undefined = Object.entries(map).find(([key]) => { return key === levelName })
      if (found) {
        return found[1]
      }
      return ''
    }
}

</script>
