import { boot } from 'quasar/wrappers'

declare module 'vue/types/vue' {
  interface Vue {
    $window: Window;
  }
}

export default boot(({ Vue }) => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  Vue.prototype.$window = window
})
