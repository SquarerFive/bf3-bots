<template>
    <div>
        <q-item v-if="dark">
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

@Component({ components: { } })
export default class AssetComponent extends Vue {
    @Prop({ required: true, default: defaultGameAsset }) asset!: GameAsset
    @Prop({ required: true, default: [] }) outSelectedAssets!: GameAsset[]
    @Prop({ required: true, type: Boolean, default: true }) add!: boolean
    @Prop({ required: false, type: Boolean, default: true }) dark!: boolean
    @Prop({ required: false, default: false, type: Boolean }) disabled!: boolean
}
</script>
