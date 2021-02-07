<template>
    <q-card dark flat>
        <q-list>
            <q-item>
                <q-item-label header class="text-h5" style="text-align: center">
                    {{name}}
                </q-item-label>
            </q-item>
            <q-item>
                <q-item-label caption style='color: #989898'>
                    Primary
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAssetFn(kit.primary_weapon)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -20px">
                <q-card bordered flat dark style="position: relative;">
                    <q-scroll-area style="height: 100px; width: 32vh">
                    <q-card-section>
                        <q-list>
                            <q-item padding="none" v-for="asset in kit.primary_weapon" :key="asset.id" dense style="margin:0; padding: 0; width: 100%">
                                <asset-component style="width: 100%" :add="false" :asset="asset" :outSelectedAssets="kit.primary_weapon" />
                            </q-item>
                        </q-list>
                    </q-card-section>
                    </q-scroll-area>
                </q-card>
            </q-item>

            <q-item>
                <q-item-label caption style='color: #989898'>
                    Secondary
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAssetFn(kit.secondary_weapon)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -20px">
                <q-card bordered flat dark style="position: relative;">
                    <q-scroll-area style="height: 100px; width: 32vh">
                    <q-card-section>
                        <q-list>
                            <q-item padding="none" v-for="asset in kit.secondary_weapon" :key="asset.id" dense style="margin:0; padding: 0">
                                <asset-component style="width: 100%" :add="false" :asset="asset" :outSelectedAssets="kit.secondary_weapon" />
                            </q-item>
                        </q-list>
                    </q-card-section>
                    </q-scroll-area>
                </q-card>
            </q-item>

            <q-item>
                <q-item-label caption style='color: #989898'>
                    Primary Gadget
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAssetFn(kit.primary_gadget)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -20px">
                <q-card bordered flat dark style="position: relative;">
                    <q-scroll-area style="height: 100px; width: 32vh">
                    <q-card-section>
                        <q-list>
                            <q-item padding="none" v-for="asset in kit.primary_gadget" :key="asset.id" dense style="margin:0; padding: 0">
                                <asset-component style="width: 100%" :add="false" :asset="asset" :outSelectedAssets="kit.primary_gadget" />
                            </q-item>
                        </q-list>
                    </q-card-section>
                    </q-scroll-area>
                </q-card>
            </q-item>

            <q-item>
                <q-item-label caption style='color: #989898'>
                    Secondary Gadget
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAssetFn(kit.secondary_gadget)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -20px">
                <q-card bordered flat dark style="position: relative;">
                    <q-scroll-area style="height: 100px; width: 32vh">
                    <q-card-section>
                        <q-list>
                            <q-item padding="none" v-for="asset in kit.secondary_gadget" :key="asset.id" dense style="margin:0; padding: 0">
                                <asset-component style="width: 100%" :add="false" :asset="asset" :outSelectedAssets="kit.secondary_gadget" />
                            </q-item>
                        </q-list>
                    </q-card-section>
                    </q-scroll-area>
                </q-card>
            </q-item>

            <q-item>
                <q-item-label caption style='color: #989898'>
                    Melee
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAssetFn(kit.melee)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -20px">
                <q-card bordered flat dark style="position: relative;">
                    <q-scroll-area style="height: 100px; width: 32vh">
                    <q-card-section>
                        <q-list>
                            <q-item padding="none" v-for="asset in kit.melee" :key="asset.id" dense style="margin:0; padding: 0">
                                <asset-component style="width: 100%" :dark="true" :add="false" :asset="asset" :outSelectedAssets="kit.melee" />
                            </q-item>
                        </q-list>
                    </q-card-section>
                    </q-scroll-area>
                </q-card>
            </q-item>
            <q-item>
                <q-item-label caption style='color: #989898'>
                    Appearance
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAssetFn(kit.appearance)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -20px">
                <q-card bordered flat dark style="position: relative;">
                    <q-scroll-area style="height: 100px; width: 32vh">
                    <q-card-section>
                        <q-list>
                            <q-item padding="none" v-for="asset in kit.appearance" :key="asset.id" dense style="margin:0; padding: 0">
                                <asset-component style="width: 100%" :dark="true" :add="false" :asset="asset" :outSelectedAssets="kit.appearance" />
                            </q-item>
                        </q-list>
                    </q-card-section>
                    </q-scroll-area>
                </q-card>
            </q-item>
            <q-item>
                <q-item-label caption style='color: #989898'>
                    Kit Asset
                </q-item-label>
                <q-space />
                <q-item-label>
                    <q-btn dense icon="add" flat size='12px' color="grey-6" padding="none" @click="onRequestAddAssetFn(kit.kit_assets, true)"/>
                </q-item-label>
            </q-item>
            <q-item style="width: 100%; margin-top: -20px">
                <q-card bordered flat dark style="position: relative;">
                    <q-scroll-area style="height: 100px; width: 32vh">
                    <q-card-section>
                        <q-list>
                            <q-item padding="none" dense style="margin:0; padding: 0" v-for="asset in kit.kit_assets" :key="asset.name">
                                <asset-component style="width: 100%" :dark="true" :add="false" :asset="asset" :outSelectedAssets="kit.kit_assets" />
                            </q-item>
                        </q-list>
                    </q-card-section>
                    </q-scroll-area>
                </q-card>
            </q-item>
        </q-list>
    </q-card>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import AssetComponent from 'components/AssetComponent.vue'
import { defaultSoldierKit, GameAsset, Manager, SoldierKit } from 'src/store/models'

@Component({ components: { AssetComponent } })
export default class SoldierKitComponent extends Vue {
    @Prop({ required: true, type: Function }) onRequestAddAsset!: CallableFunction
    @Prop({ required: true, type: String }) name!: string
    @Prop({ required: true, default: defaultSoldierKit }) kit!: SoldierKit
    @Prop({ required: true }) manager!: Manager
    // kit: SoldierKit = defaultSoldierKit
    primary: GameAsset[] = []
    secondary: GameAsset[] = []
    gadget1: GameAsset[] = []
    gadget2: GameAsset[] = []
    melee: GameAsset[] = []

    kitAssetArray : GameAsset[] = []
    onRequestAddAssetFn (assetArray : GameAsset[], isKitAsset = false) {
      this.manager.currentAssetSelection = assetArray
      this.onRequestAddAsset(assetArray, isKitAsset)
      // this.$emit('onRequestAddAsset', assetArray)
    }
}

</script>
