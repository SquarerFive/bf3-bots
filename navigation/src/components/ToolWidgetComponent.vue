<template>
  <q-btn dense flat style="padding:0;margin:0;text-align:left" :to="to">
    <q-card v-ripple class="my-card cursor-pointer q-hoverable" style="min-width: 300px;padding:0;margin:0">
      <span class="q-focus-helper"></span>
      <q-img src="https://media.discordapp.net/attachments/532770468277780510/802070596871258142/unknown.png">
        <div class="absolute-bottom text-left">
          <div class="text-h6">{{toolName}}</div>
          <div class="text-subtitle3" style="font-weight: 0; font-family: 'Roboto' sans-serif">Tool</div>
        </div>
      </q-img>
    </q-card>
  </q-btn>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Prop } from 'vue-property-decorator'

@Component
export default class ToolWidgetComponent extends Vue {
  @Prop({
    default: console.log, required: false
  }) readonly onClick!: CallableFunction;

  @Prop({
    default: '#', required: false
  }) readonly to!: string;

  @Prop({
    default: 'BF3 Project Tool Component', required: true
  }) readonly toolName!: string;
}
</script>
