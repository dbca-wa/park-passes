<template>
  <div class="position-absolute w-100 h-100 d-flex flex-column align-items-center bg-white justify-content-center">
    <div class="spinner spinner-border org-primary" style="width: 3rem; height: 3rem;" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script>
export default {
  name:'BootstrapSpinner',
  props:{
      isLoading:{
          default:function () {
              return false;
          }
      }
  }
}
</script>

<style lang="css">
  .spinner {
    display: block;
    position: fixed;
    z-index: 1031; /* High z-index so it is on top of the page */
    top: 50%;
    right: 50%; /* or: left: 50%; */
    /*margin-top: -..px;  half of the elements height */
   /* margin-right: -..px;  half of the elements width */
  }
</style>
