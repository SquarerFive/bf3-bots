<template>
  <q-dialog v-model="loginOpened" style="height:55vh;width:500px;">
    <q-card style="height: 52vh;width:500px;">
      <q-tabs
        v-model="tab"
        inline-label
        class="text-dark shadow-2"
      >
        <q-tab name="login" icon="mail" label="Login" />
        <q-tab name="register" icon="alarm" label="Register" />
      </q-tabs>

      <q-card-section>
        <div class="text-h6">{{getTabName()}}</div>
      </q-card-section>
      <q-card-section class="q-pt-none" v-if="tab=='login'">

        <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md" >
          <q-input
            filled
            v-model="username"
            label="Username"
            hint="Your username"
            lazy-rules
            :rules="[
              (val) => (val && val.length > 0) || 'Please type something',
            ]"
          />

          <q-input
            filled
            type="password"
            v-model="password"
            label="Password"
            lazy-rules

          />

          <q-toggle v-model="remember" label="Remember me" />

        </q-form>
      </q-card-section>

      <q-card-section class="q-pt-none" v-if="tab=='register'">
        <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
          <q-input
            filled
            type="email"
            v-model="email"
            label="Email address"
            hint="Your email"
          />
          <q-input
            filled
            v-model="username"
            label="Username"
            hint="Your username"
            lazy-rules
            :rules="[
              (val) => (val && val.length > 0) || 'Please type something',
            ]"
          />

          <q-input
            filled
            type="password"
            v-model="password"
            label="Password"
            lazy-rules
            @submit="onSubmit"
            />
            <q-input
            filled
            v-model="description"
            label="User Description"
            lazy-rules
            />
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Submit" color="primary" v-close-popup @click="onSubmit"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { Manager } from '../store/models'
import { ManagerStore } from '../store/ManagerStoreModule'

@Component
export default class LoginComponent extends Vue {
  tab = 'login';
  remember = false;
  username = '';
  password = '';
  email = '';
  description = '';

  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  manager : Manager|undefined;

  mounted () {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
    this.manager = new Manager(this)
  }

  get loginOpened () {
    // console.log("loginOpened", (<State>(this.$store.state).player.loginOpened));
    return ManagerStore.loginOpened // (<State> this.$store.state).player.loginOpened
  }

  set loginOpened (newValue: boolean) {
    // this.$store.commit('player/updateLoginOpened', newValue)
    ManagerStore.setLoginOpened(newValue)
  }

  getTabName () {
    const tabName = this.tab
    return tabName.charAt(0).toUpperCase() + tabName.slice(1)
  }

  onReset () {
    // todo
  }

  onSubmit () {
    if (this.tab === 'register') {
      this.$axios.post('http://localhost:8000/pathfinding/register-user/', {
        username: this.username,
        email: this.email,
        password: this.password,
        description: this.description
      }).then(resp => {
        console.log(resp.data)
        this.tab = 'login'
        this.onSubmit()
      }).catch(error => {
        console.log(error)
      })
    } else {
      if (this.manager) {
        console.log('calling login, for', this.manager, this.username, this.password)
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
        this.manager.login(this.username, this.password).catch(e => {
          console.log('failed to login :( ', e)
        })
      }
    }
  }
}
</script>
