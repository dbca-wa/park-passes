<template>
  <div class="container" id="internalDash">
    <div v-if="is_debug">src/components/internal/Dashboard.vue</div>

    <div class="tab-content" id="pills-tabContent">
      <div
        class="tab-pane active"
        id="pills-retailer-group-users"
        role="tabpanel"
        aria-labelledby="pills-retailer-group-users-tab"
      >
        <FormSection
          :formCollapse="false"
          label="Retail Users"
          Index="retailer-group-users"
        >
          <RetailerGroupUsersDatatable
            ref="retailerGroupUserDatatable"
            level="internal"
          />
        </FormSection>
      </div>
      <div
        class="tab-pane active"
        id="pills-retailer-group-users"
        role="tabpanel"
        aria-labelledby="pills-retailer-group-users-tab"
      >
        <FormSection
          :formCollapse="false"
          label="Retail User Invites"
          Index="retailer-group-user-invites"
        >
          <RetailerGroupUserInvitesDatatable
            ref="retailerGroupUserInvitesDatatable"
            level="internal"
            @approvalProcessed="approvalProcessed"
          />
        </FormSection>
      </div>
    </div>
  </div>
</template>

<script>
import FormSection from "@/components/forms/SectionToggle.vue";
import RetailerGroupUsersDatatable from "@/components/internal/datatables/RetailerGroupUsersDatatable";
import RetailerGroupUserInvitesDatatable from "@/components/internal/datatables/RetailerGroupUserInvitesDatatable";

export default {
  name: "RetailerGroupUsers",
  data() {
    let vm = this;
    return {
      accessing_user: null,
    };
  },
  components: {
    FormSection,
    RetailerGroupUsersDatatable,
    RetailerGroupUserInvitesDatatable,
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
    is_internal: function () {
      return this.level == "internal";
    },
  },
  methods: {
    approvalProcessed: function () {
      this.$refs.retailerGroupUserDatatable.draw();
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
