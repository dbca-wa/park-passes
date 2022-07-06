<template>
<div id="app">
  <router-view :key="$route.fullPath"></router-view>
</div>
</template>

<script>
export default {
  name: 'app'
}


</script>

<style>
.popover {
    max-width: 100% !important;
}
.select2-container--disabled, .select2-container--focus{
    z-index: 1;
}
</style>
