<template>
    <button disabled>
        <div class="spinner-border spinner-border-sm text-light" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </button>
</template>

<script>

export default {
    name:'BootstrapButtonSpinner',
    props:{
        isLoading:{
            default:function () {
                return false;
            }
        }
    }
}
</script>
