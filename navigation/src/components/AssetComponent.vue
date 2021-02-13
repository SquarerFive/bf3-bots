<template>
    <div>
        <q-item v-if="dark" :clickable="clickable" :active="selected" @click="onClick(asset)">
            <q-item-section avatar v-if="selectable">
                <q-checkbox :value="actionSelectedAssets.findIndex(el => { return el.path === asset.path }) > -1" @input="onClickActionSelect" />
            </q-item-section>
            <q-item-section>
                <q-item-label>{{ asset.name }}</q-item-label>
                    <q-item-label dark caption style="color: #989898">
                        {{ asset.path }}
                    </q-item-label>
                </q-item-section>
            <q-item-section avatar>
                <div v-if="add">
                    <q-btn icon="add" color="positive" :disable="disabled" @click="outSelectedAssets.push(asset)">
                    </q-btn>
                </div>
                <div v-if="!add">
                    <q-btn icon="remove" color="negative" @click="outSelectedAssets.splice(outSelectedAssets.indexOf(asset), 1)">
                    </q-btn>
                </div>
            </q-item-section>
        </q-item>
        <q-item v-if="!dark">
            <q-item-section>
                <q-item-label>{{ asset.name }}</q-item-label>
                    <q-item-label caption>
                        {{ asset.path }}
                    </q-item-label>
                </q-item-section>
            <q-item-section avatar>
                <div v-if="add">
                    <q-btn icon="add" color="positive" @click="outSelectedAssets.push(asset)">
                    </q-btn>
                </div>
                <div v-if="!add">
                    <q-btn icon="remove" color="negative" @click="outSelectedAssets.splice(outSelectedAssets.indexOf(asset), 1)">
                    </q-btn>
                </div>
            </q-item-section>
        </q-item>
    </div>
</template>

<script lang="ts">
import { defaultGameAsset, GameAsset } from 'src/store/models'
import { Vue, Component, Prop } from 'vue-property-decorator'

function defaultClickFn (asset : GameAsset) {
  if (asset) {
    return asset.id === 0
  }
  return false
}

@Component({ components: { } })
export default class AssetComponent extends Vue {
    @Prop({ required: true, default: defaultGameAsset }) asset!: GameAsset
    @Prop({ required: true, default: [] }) outSelectedAssets!: GameAsset[]
    @Prop({ required: false }) actionSelectedAssets!: GameAsset[]
    @Prop({ required: true, type: Boolean, default: true }) add!: boolean
    @Prop({ required: false, type: Boolean, default: true }) dark!: boolean
    @Prop({ required: false, default: false, type: Boolean }) disabled!: boolean
    @Prop({ required: false, default: true, type: Boolean }) selectable!: boolean
    @Prop({ required: false, default: false, type: Boolean }) clickable!: boolean
    @Prop({ required: false, default: false, type: Boolean }) selected!: boolean
    @Prop({ required: false, default: defaultClickFn }) onClick!: CallableFunction

    onClickActionSelect () {
      if (this.actionSelectedAssets.findIndex(el => { return el.path === this.asset.path }) === -1) {
        this.actionSelectedAssets.push(this.asset)
      } else {
        this.actionSelectedAssets.splice(this.actionSelectedAssets.findIndex(el => { return el.path === this.asset.path }), 1)
      }
    }
}
</script>
