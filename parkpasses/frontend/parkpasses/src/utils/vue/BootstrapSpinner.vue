<template>
  <div v-if="centerOfScreen" class="position-absolute w-100 h-100 d-flex flex-column align-items-center bg-white justify-content-center">
    <div :class="spinnerClass" class="spinner spinner-border org-primary" style="width: 3rem; height: 3rem;" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
  <div v-else>
    <div :class="spinnerClass" class="spinner-border org-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script>
export default {
  name:'BootstrapSpinner',
  props:{
      isLoading:{
          type: Boolean,
          default: false
      },
      centerOfScreen:{
          type: Boolean,
          default: true
      },
      small:{
          type: Boolean,
          default: false
      },
  },
  data: function () {
    return {
    };
  },
  computed: {
    spinnerClass: function () {
      let className = 'spinner-center-screen';
      if(!this.centerOfScreen){
        className = 'spinner-center-component';
      }
      if(this.small){
        className += ' spinner-border-sm';
      }
      return className;
    },
  },
}
</script>

<style lang="css">
  .spinner-center-screen {
    display: block;
    position: fixed;
    z-index: 1031; /* High z-index so it is on top of the page */
    top: 50%;
    right: 50%; /* or: left: 50%; */
    /*margin-top: -..px;  half of the elements height */
   /* margin-right: -..px;  half of the elements width */
  }

  .spinner-center-component {
    margin-top:50px;
    margin-left:140px;
  }
</style>
