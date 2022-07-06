<template>
    <div class="container" id="shopHome">
        <div class="row">
            <div class="col-4">

                <ShopSideMenu activeItem=0 />

            </div>
            <div class="col">
                <h1>Buy a Park Pass Voucher</h1>

                <p>
                    Enter the details of the person receiving the voucher, the voucher details
                    and your own details and we will send the couvher with your text to the
                    recipient at the selected date.
                </p>

                <div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="amount" class="col-form-label">Voucher Amount</label>
                        </div>
                        <div class="col-auto">
                            <input type="number" id="amount" name="amount" class="form-control" ref="amount" min="5" value="5" step="5" required="required" autofocus>
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="recipientName" class="col-form-label">Recipient Name</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="recipientName" name="recipientName" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="recipientEmail" class="col-form-label">Recipient Email Address</label>
                        </div>
                        <div class="col-auto">
                            <input type="email" id="recipientEmail" name="recipientEmail" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="confirmRecipientEmail" class="col-form-label">Confirm Recipient Email Address</label>
                        </div>
                        <div class="col-auto">
                            <input type="email" id="confirmRecipientEmail" name="confirmRecipientEmail" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="personalMessage" class="col-form-label">Message to Recipient</label>
                        </div>
                        <div class="col-auto">
                            <textarea id="personalMessage" name="personalMessage" class="form-control" required="required"></textarea>
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="datetimeToEmail" class="col-form-label">Date to Send the Voucher</label>
                        </div>
                        <div class="col-auto">
                            <input type="date" id="datetimeToEmail" name="datetimeToEmail" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="firstName" class="col-form-label">First Name</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="firstName" name="firstName" class="form-control" ref="firstName" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="lastName" class="col-form-label">Last Name</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="lastName" name="lastName" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="email" class="col-form-label">Your Email Address</label>
                        </div>
                        <div class="col-auto">
                            <input type="email" id="email" name="email" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="confirmEmail" class="col-form-label">Confirm Your Email</label>
                        </div>
                        <div class="col-auto">
                            <input type="email" id="confirmEmail" name="confirmEmail" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="postcode" class="col-form-label">Your Postcode</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="postcode" name="postcode" class="form-control" pattern="[0-9]{4}" required="required">
                        </div>
                    </div>
                    <div class="row g-3mb-2">
                        <div class="col-md-4">
                            &nbsp;
                        </div>
                        <div class="col-auto">
                            <button @click="submitForm" class="btn btn-primary px-5" type="submit">Pay</button>
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
    name: "PurchasePass",
    data: function () {
        return {
            voucher: {},
        };
    },
    components: {
        ShopSideMenu
    },
    computed: {

    },
    methods: {

    },
    created: function () {

    },
    mounted: function () {
        this.$refs.amount.focus();
    }
};
</script>

<style scoped>

</style>
