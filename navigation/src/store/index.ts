import { store } from 'quasar/wrappers'
import Vuex, { Store } from 'vuex'

import manager from './manager'
import { ManagerStateInterface } from './manager/state'
// import example from './module-example';
// import { ExampleStateInterface } from './module-example/state';

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation
 */

export let storeInstance: Store<unknown>

export interface StateInterface {
  // Define your own store structure, using submodules if needed
  // example: ExampleStateInterface;
  // Declared as unknown to avoid linting issue. Best to strongly type as per the line above.
  example: unknown;
  manager: ManagerStateInterface
}

export default store(function ({ Vue }) {
  Vue.use(Vuex)

  const store_ = new Vuex.Store<StateInterface>({
    modules: {
      // example
      manager
    },

    // enable strict mode (adds overhead!)
    // for dev mode only
    strict: !!process.env.DEBUGGING
  })
  storeInstance = store_
  return store_
})
