<template>
    <q-item>
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
</template>

<script lang="ts">
import { defaultGameAsset, GameAsset } from 'src/store/models'
import { Vue, Component, Prop } from 'vue-property-decorator'

@Component({ components: { } })
export default class AssetComponent extends Vue {
    @Prop({ required: true, default: defaultGameAsset }) asset!: GameAsset;
    @Prop({ required: true, default: [] }) outSelectedAssets!: GameAsset[];
    @Prop({ required: true, type: Boolean, default: true }) add!: boolean;
}
</script>
