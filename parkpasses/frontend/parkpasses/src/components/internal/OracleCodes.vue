<template>
  <div class="container" id="internalOracleCodes">

    <div class="tab-content" id="pills-tabContent">
      <div
        class="tab-pane active"
        id="pills-district-based-oracle-codes"
        role="tabpanel"
        aria-labelledby="pills-district-based-oracle-codes-tab"
      >
        <FormSection
          :formCollapse="false"
          label="District-Based Oracle Codes"
          Index="district-based-oracle-codes"
        >

        <div>
            <div v-for="district in districts" :key="district">
              <div class="card mb-3">
                <img src="" class="card-img-top" alt="">
                <div class="card-body">
                  <h5 class="card-title"><h2>{{ district }}</h2></h5>
                  <p class="card-text">
                    <div>
                      <div v-for="passType in passTypes">
                        <div class="card mb-3 w-50">
                          <img src="" class="card-img-top" alt="">
                          <div class="card-body">
                            <h5 class="card-title">{{ passType.name }}</h5>
                            <p class="card-text">
                              <div v-if="passType.options && passType.options.length > 0">
                                <table class="table table-sm">
                                  <thead>
                                    <tr>
                                      <th scope="col" class="w-50">Pass Duration</th>
                                      <th scope="col">Oracle Code</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr v-for="option in passType.options">
                                      <th scope="row">{{ option.name }}</th>
                                      <td><input class="form-control" type="text" /></td>
                                    </tr>
                                  </tbody>
                                </table>
                              </div>
                            </p>
                          </div>
                        </div>
                      </div>
                  </div>
                  </p>
                  <button @click="" class="btn licensing-btn-primary">Save</button>
                </div>
              </div>



            </div>
        </div>

        </FormSection>
      </div>
    </div>
  </div>
</template>

<script>
import FormSection from "@/components/forms/SectionToggle.vue";

export default {
    name: "InternalOracleCodes",
    data() {
        let vm = this;
        return {
            districts: [
              'Alpine',
              'Bonneville',
              'Box Elder',
              'Cache',
              'Carbon',
              'Daggett',
              'Davis',
              'Duchesne',
              'Emery',
              'Garfield',
              'Grand',
              'Iron',
              'Juab',
            ],
            passTypes: [{
                "name":"WA Holiday Park Pass",
                options:[
                  {"name":"5 Days","Duration":5},
                  {"name":"14 Days","Duration":14},
                  {"name":"28 Days","Duration":28},
                ]
              }, {
                "name":"All Park Pass",
                options:[
                  {"name":"Annual","Duration":365},
                ]
              }
            ]
        };
    },
    components: {
        FormSection,
    },
    computed: {

    },
    methods: {

    },
    mounted: async function () {

    },
    created: function () {

    },
};
</script>

<style lang="css" scoped>
.section {
  text-transform: capitalize;
}
.list-group {
  margin-bottom: 0;
}
.fixed-top {
  position: fixed;
  top: 56px;
}

.nav-item {
  margin-bottom: 2px;
}

.nav-item > li > a {
  background-color: yellow !important;
  color: #fff;
}

.nav-item > li.active > a,
.nav-item > li.active > a:hover,
.nav-item > li.active > a:focus {
  color: white;
  background-color: blue;
  border: 1px solid #888888;
}

.admin > div {
  display: inline-block;
  vertical-align: top;
  margin-right: 1em;
}
.nav-pills .nav-link {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  border-top-left-radius: 0.5em;
  border-top-right-radius: 0.5em;
  margin-right: 0.25em;
}
.nav-pills .nav-link {
  background: lightgray;
}
.nav-pills .nav-link.active {
  background: gray;
}
</style>
