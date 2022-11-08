<template>
  <div class="container" id="externalDash">
    <div v-if="is_debug">src/components/external/Dashboard.vue</div>

    <div class="tab-content" id="pills-tabContent">
      <div
        class="tab-pane active"
        id="pills-orders"
        role="tabpanel"
        aria-labelledby="pills-orders-tab"
      >
        <FormSection
          :formCollapse="false"
          label="Your Orders"
          Index="orders"
        >
          <OrdersDatatable
            ref="ordersDatatable"
            level="external"
          />
        </FormSection>
      </div>
    </div>
  </div>
</template>

<script>
import FormSection from "@/components/forms/SectionToggle.vue";
import OrdersDatatable from "@/components/external/datatables/OrdersDatatable.vue";

export default {
  name: "externalDashboard",
  data() {
    let vm = this;
    return {
      accessing_user: null,
    };
  },
  components: {
    FormSection,
    OrdersDatatable,
  },
  watch: {},
  computed: {
    is_debug: function () {
      return this.$route.query.hasOwnProperty("debug") &&
        this.$route.query.debug == "true"
        ? true
        : false;
    },
    is_external: function () {
      return this.level == "external";
    },
    is_external: function () {
      return this.level == "external";
    },
  },
  methods: {
    tabClicked: function (param) {
      if (param == "orders") {
        this.$refs.ordersDatatable.adjustTableWidth();
      }
    },
    mapTabClicked: function () {
      this.$refs.component_map_with_filters.forceToRefreshMap();
    },
    set_active_tab: function (tab_href_name) {
      let elem = $('#pills-tab a[href="#' + tab_href_name + '"]');
      let tab = bootstrap.Tab.getInstance(elem);
      if (!tab) tab = new bootstrap.Tab(elem);
      tab.show();
    },
  },
  mounted: async function () {
    this.$nextTick(function () {
      chevron_toggle.init();
    });
  },
  created: function () {},
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
