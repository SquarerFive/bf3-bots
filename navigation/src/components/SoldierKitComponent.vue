<template>
    <q-card dark>
        <q-list>
            <q-item>
                <q-item-label header class="text-h5" style="text-align: center">
                    Assault
                </q-item-label>
            </q-item>
            <q-item>
                <q-item-label caption style='color: #989898'>
                    Primary
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAsset(primary)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -16%">
                <q-card bordered flat dark>
                    <q-card-section>
                        <q-scroll-area style="max-height: 100px">
                            <q-list>
                                <div v-for="asset in primary" :key="asset.id">
                                    <asset-component :add="false" :asset="asset" :outSelectedAssets="primary" />
                                </div>
                            </q-list>
                        </q-scroll-area>
                    </q-card-section>
                </q-card>
            </q-item>
        </q-list>
    </q-card>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import AssetComponent from 'components/AssetComponent.vue'
import { GameAsset } from 'src/store/models'

@Component({ components: { AssetComponent } })
export default class SoldierKitComponent extends Vue {
    @Prop({ required: true, type: Function }) onRequestAddAsset!: CallableFunction

    primary: GameAsset[] = []
    secondary: GameAsset[] = []
    gadget1: GameAsset[] = []
    gadget2: GameAsset[] = []
    melee: GameAsset[] = []

    onRequestAddAssetFn (assetArray : GameAsset[]) {
      this.$emit('onRequestAddAsset', assetArray)
    }
}

</script>
