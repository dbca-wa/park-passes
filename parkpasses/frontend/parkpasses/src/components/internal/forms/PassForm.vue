<template lang="html">
    <div class="container" id="internalPass">
        <div class="row">
            <h1></h1>
            <div class="col-md-3">

            </div>
            <div class="col-md-1">

            </div>
            <div class="col-md-8">
                <SectionToggle label="Park Pass - Holiday">
                    <form>
                    <div class="row mb-3">
                        <label for="name" class="col-sm-2 col-form-label">Pass Holder</label>
                        <div class="col-sm-10">
                            <span class="form-text">John Recipient</span>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="name" class="col-sm-2 col-form-label">Email Address</label>
                        <div class="col-sm-10">
                            <span class="form-text"><a target="blank" href="mailto:john@recipient.org">john@recipient.org</a></span>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="name" class="col-sm-2 col-form-label">Mobile Number</label>
                        <div class="col-sm-10">
                            <span class="form-text">0411 223 344</span>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="name" class="col-sm-2 col-form-label">Email Address</label>
                        <div class="col-sm-10">
                            <input type="text" readonly class="form-control" id="name" value="john@recipient.org" />
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-2 col-form-label">Email Address</label>
                        <div class="col-sm-10">
                            <input type="text" class="form-control" id="">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Sign in</button>
                    </form>
                </SectionToggle>
            </div>
        </div>
    </div>
</template>

<script>
import SectionToggle from '@/components/forms/SectionToggle.vue'

export default {
    name: "PassForm",
    props: {

    },
    components: {
        SectionToggle
    }
}
</script>

<style scoped>
    .form-text{
        display:block;
        padding: 0.375rem 0.75rem 0 0;
        margin:0;
        font-size:1rem;
    }
</style>
