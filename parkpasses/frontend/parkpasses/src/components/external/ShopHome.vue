<template>
  <div class="container" id="shopHome">
    <div class="row">

      <div class="col-4">

        <ShopSideMenu />

      </div>

      <div class="col">

        <h1>Park Passes</h1>

        <p class="lead">Your ticket to the natural beauty of Western Australia.</p>

        <p>Exploring Western Australia's stunning parks and reserves? Park passes offer both value for money and convenience.</p>

        <p>And why not purchase a Gift Voucher? The perfect gift for that nature lover you want to surprise!</p>

        <div class="home-options">

          <div class="card faq-card mb-3">
            <div class="row g-0">
              <div class="col-md-4">
                <img src="https://picsum.photos/id/101/300/210" class="img-fluid rounded-start" alt="Log In">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <h5 class="card-title">Log In</h5>

                  <div class="row g-3 align-items-center">
                    <div class="col-auto">
                      <label for="inputPassword6" class="col-form-label">Email</label>
                    </div>
                    <div class="col-auto">
                      <input type="email" id="inputPassword6" class="form-control" autofocus>
                    </div>
                    <div class="col-auto">
                      <button type="submit" class="btn btn-primary">Log In</button>
                    </div>
                  </div>

                  <p class="card-text">
                      <ul>
                        <li>View and download your current park pass</li>
                        <li>Update the vehicle details for your pass</li>
                        <li>Update your other details</li>
                      </ul>
                    </p>
                </div>
              </div>
            </div>
          </div>

          <div @click="redirectToFAQ()" class="card faq-card mb-3">
            <div class="row g-0">
              <div class="col-md-4">
                <img src="https://picsum.photos/id/8/300/170" class="img-fluid rounded-start" alt="Frequently Asked Questions">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <h5 class="card-title">FAQ</h5>
                  <p class="card-text">Click here for answers to common questions.</p>
                </div>
              </div>
            </div>
          </div>

          <div @click="redirectToHelp()" class="card faq-card mb-3">
            <div class="row g-0">
              <div class="col-md-4">
                <img src="https://picsum.photos/id/7/300/170" class="img-fluid rounded-start" alt="Help">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <h5 class="card-title">Help</h5>
                  <p class="card-text">Click here for help if you want to update your vehicle details or if you did not receive your park pass.</p>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { api_endpoints } from '@/utils/hooks'
import ShopSideMenu from '@/components/external/ShopSideMenu.vue'

export default {
    name: "ShopHome",
    data: function () {
        return {
            passTypes: [],
            errorMessage: null
        };
    },
    components: {
        api_endpoints,
        ShopSideMenu,
    },
    methods: {
        redirectToFAQ: function() {
            window.location.href = 'faq/'
        },
        redirectToHelp: function() {
            window.location.href = 'help/'
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
}

.card:hover {
  cursor: pointer;
  opacity: 0.8;
}
</style>
