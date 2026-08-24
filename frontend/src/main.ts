import { createApp } from 'vue';
import { IonicVue } from '@ionic/vue';
import App from './App.vue';

/* Core CSS required for Ionic components to work properly */
import '@ionic/vue/css/core.css';

const app = createApp(App);
app.use(IonicVue);
app.mount('#app');
