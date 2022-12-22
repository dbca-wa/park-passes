<template>
    <div>
        <h1>Park Passes</h1>

        <p class="lead">Your ticket to the natural beauty of Western Australia.</p>

        <p>Exploring Western Australia's stunning parks and reserves? Park passes offer both value for money and convenience.</p>

        <p class="mb-4">And why not purchase a Gift Voucher? The perfect gift for that nature lover you want to surprise!</p>

        <div class="home-options">

          <div v-if="store.userData && store.userData.is_authenticated" @click="redirectToSSOLogout()" class="card login-card mb-4">
            <div class="row g-0">
              <div class="col-12 col-sm-12 col-md-12 col-lg-5 col-xl-3 offset-md-1 offset-lg-0">
                <i class="fa-solid fa-door-open org-icon-primary fa-7x pt-3 ps-4" title="Logout"></i>
              </div>
              <div class="col-12 col-sm-12 col-md-12 col-lg-7">
                <div class="card-body">
                  <h5 class="card-title">Log Out</h5>
                  <p class="card-text">
                      <ul>
                        <li><a href="/your-park-passes">View and download your current park pass</a></li>
                        <li><a href="/your-park-passes">Update the vehicle details for your pass</a></li>
                        <li><a href="/ledger-ui/accounts">Update your account details</a></li>
                      </ul>
                    </p>
                </div>
              </div>
            </div>
          </div>

          <div v-else @click="redirectToSSOLogin()" class="card login-card mb-4">
            <div class="row g-0">
              <div class="col-12 col-sm-12 col-md-12 col-lg-5 col-xl-3 offset-md-1 offset-lg-0">
                <i class="fa-solid fa-door-open org-icon-primary fa-7x ps-4" title="Login"></i>
              </div>
              <div class="col-12 col-sm-12 col-md-12 col-lg-7">
                <div class="card-body">
                  <h5 class="card-title">Log In</h5>

                  <p class="card-text align-items-center">
                      <ul>
                        <li>View and download your current park pass</li>
                        <li>Update the vehicle details for your pass</li>
                        <li>Update your account details</li>
                      </ul>
                    </p>
                </div>
              </div>
            </div>
          </div>

          <div @click="redirectToFAQ()" class="card faq-card mb-4">
            <div class="row g-0 align-items-center">
              <div class="col-12 col-sm-12 col-md-12 col-lg-5 col-xl-3 offset-md-1 offset-lg-0">
                <i class="fa-solid fa-circle-info org-icon-primary fa-7x ps-4" title="Frequently Asked Questions"></i>
              </div>
              <div class="col-12 col-sm-12 col-md-12 col-lg-7">
                <div class="card-body">
                  <h5 class="card-title">FAQ</h5>
                  <p class="card-text">Click here for answers to common questions.</p>
                </div>
              </div>
            </div>
          </div>

          <div @click="redirectToHelp()" class="card help-card mb-4">
            <div class="row g-0 align-items-center">
              <div class="col-12 col-sm-12 col-md-12 col-lg-5 col-xl-3 offset-md-1 offset-lg-0">
                <i class="fa-solid fa-circle-question org-icon-primary fa-7x ps-4" title="Help"></i>
              </div>
              <div class="col-12 col-sm-12 col-md-12 col-lg-6">
                <div class="card-body">
                  <h5 class="card-title">Help</h5>
                  <p class="card-text">Click here for help if you want to update your vehicle details or if you did not receive your park pass.</p>
                </div>
              </div>
            </div>
          </div>

        </div>
    </div>
</template>

<script>
import { useStore } from '@/stores/state'

export default {
    name: "HomeContent",
    data: function () {
        return {
            store: useStore(),
        };
    },
    methods: {
        redirectToFAQ: function() {
            window.location.href = '/faq/';
        },
        redirectToHelp: function() {
            window.location.href = '/help/';
        },
        redirectToSSOLogin: function() {
            window.location.href = '/ssologin';
        },
        redirectToSSOLogout: function() {
            window.location.href = '/logout/?next=/';
        }
    },
};
</script>

<style scoped>
.card-text ul {
  margin:10px 0 0 0;
  font-size:.9em;
}

.card {
  opacity: 1;
  border:0;
  cursor:pointer;
}

.card:hover {
  cursor: pointer;
  opacity: 0.8;
}

.login-card .card-text ul {
  margin: 0 0 0 0;
}

</style>
