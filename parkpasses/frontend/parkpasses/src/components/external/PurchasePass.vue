<template>
        <div>
            <div v-if="passType">
                <div v-if="passType">
                    <h1 v-if="isRetailer">Sell a {{passType.display_name}}</h1>
                    <h1 v-else>Buy {{indefiniteArticle}} {{passType.display_name}}</h1>
                </div>

                <div v-if="isRetailer" class="pb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
                        <symbol id="check-circle-fill" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                        </symbol>
                        <symbol id="info-fill" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
                        </symbol>
                        <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                        </symbol>
                        </svg>
                        <div class="alert alert-primary d-flex align-items-center" role="alert">
                            <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:"><use xlink:href="#info-fill"/></svg>
                            <div>
                                <div>Enter the customer's details below and then click 'Next'</div>
                            </div>
                        </div>
                    </div>
                <div v-else v-html="passType.description"></div>

                <div>
                    <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="firstName" class="col-form-label">First Name</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="firstName" name="firstName" v-model="pass.first_name" class="form-control" ref="firstName" required="required" autofocus>
                                <div class="invalid-feedback">
                                    Please enter your first name.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="lastName" class="col-form-label">Last Name</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="lastName" name="lastName" v-model="pass.last_name" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter your last name.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="email" class="col-form-label">Your Email Address</label>
                            </div>
                            <div class="col-auto">
                                <input type="email" id="email" name="email" ref="email" v-model="pass.email" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid email address.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="confirmEmail" class="col-form-label">Confirm Your Email</label>
                            </div>
                            <div class="col-auto">
                                <input @change="validateConfirmEmail" type="email" id="confirmEmail" name="confirmEmail" ref="confirmEmail" v-model="confirmEmail" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please make sure your confirmation email matches your email.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="mobile" class="col-form-label">Mobile Number</label>
                            </div>
                            <div class="col-auto">
                                <input type="tel" id="mobile" name="mobile" v-model="pass.mobile" class="form-control" pattern="[0-9]{4}[0-9]{3}[0-9]{3}" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid mobile phone number.
                                </div>
                            </div>
                        </div>
                        <div v-if="isPinjarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="driversLicenceNumber" class="col-form-label">Driver's Licence Number</label>
                            </div>
                            <div class="col-auto">
                                <input type="tel" id="driversLicenceNumber" name="driversLicenceNumber" v-model="pass.drivers_licence_number" class="form-control" pattern="[a-zA-Z0-9]{8}" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid driver's licence number.
                                </div>
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="company" class="col-form-label">Company</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="company" name="company" v-model="pass.company" class="form-control">
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="address" class="col-form-label">Address</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="address" name="address" v-model="pass.address" class="form-control" required="required">
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="suburb" class="col-form-label">Town / Suburb</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="suburb" name="suburb" v-model="pass.suburb" class="form-control" required="required">
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="state" class="col-form-label">State</label>
                            </div>
                            <div class="col-auto">
                                <select id="state" name="state" v-model="pass.state" class="form-select" required="required">
                                    <option value="WA" selected="selected">Western Australia</option>
                                    <option value="NSW">New South Wales</option>
                                    <option value="VIC">Victoria</option>
                                    <option value="QLD">Queensland</option>
                                    <option value="SA">South Australia</option>
                                    <option value="ACT">Australian Capital Territory</option>
                                    <option value="TAS">Tasmania</option>
                                    <option value="NT">Northern Territory</option>
                                </select>
                            </div>
                        </div>
                        <div v-if="isAnnualLocalPass || isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="postcode" class="col-form-label">Your Postcode</label>
                            </div>
                            <div class="col-auto">
                                <input v-if="isAnnualLocalPass" @keyup="validatePostcode" @change="validatePostcode" type="text" id="postcode" name="postcode" ref="postcode" v-model="pass.postcode" class="form-control" pattern="6[0-9]{3}" required="required" minlength="4" maxlength="4">
                                <input v-else type="text" id="postcode" name="postcode" ref="postcode" v-model="pass.postcode" class="form-control" pattern="[0-9]{4}" required="required" minlength="4" maxlength="4">
                                <div v-if="!noParkForPostcodeError" class="invalid-feedback">
                                    Please enter a valid postcode.
                                </div>
                                <div v-else="noParkForPostcodeError" class="org-error-message">
                                    {{noParkForPostcodeError}}
                                </div>
                                <span v-if="loadingParkGroups" class="spinner-border-sm org-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </span>
                            </div>
                        </div>
                        <div v-if="parkGroups && parkGroups.length && pass.park_group" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="parkGroup" class="col-form-label">Park Group</label>
                            </div>
                            <div class="col-auto">
                                <select v-if="parkGroups.length>1" @change="updateParkGroup" v-model="pass.park_group_id" ref="parkGroup" id="parkGroup" name="parkGroup" class="form-select" aria-label="Park Group" required="required">
                                    <option v-for="parkGroup in parkGroups" :value="parkGroup.id" :key="parkGroup.id">{{parkGroup.name}}</option>
                                </select>
                                <span v-else>{{pass.park_group.name}}</span>
                            </div>
                        </div>
                        <div v-if="showParksList" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="parkGroup" class="col-form-label">Parks Included</label>
                            </div>
                            <div class="col-auto">
                                <ul class="parks-list">
                                    <li v-for="park in pass.park_group.parks" class="park"><span class="badge">{{ park.name }}</span></li>
                                </ul>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="concession" class="col-form-label">Elibible for Concession</label>
                            </div>
                            <div class="col-auto">
                                <div class="form-switch">
                                    <input @change="resetPrice" class="form-check-input pl-2 org-form-switch-primary" type="checkbox" id="concession" name="concession" v-model="eligibleForConcession">
                                </div>
                            </div>
                        </div>
                        <div v-if="eligibleForConcession" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="postcode" class="col-form-label">Concession Type</label>
                            </div>
                            <div class="col-auto">
                                <select @change="updateConcessionDiscount" id="concessionType" name="concessionType" v-model="pass.concession_id" class="form-select" aria-label="Concession Type" required="required">
                                    <option disabled value="0" selected>Select The Concession Type</option>
                                    <option v-for="concession in concessions" :value="concession.id" :key="concession.id">{{concession.concession_type}} ({{concession.discount_percentage}}% Discount)</option>
                                </select>
                            </div>
                        </div>
                        <div v-if="eligibleForConcession" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="concessionCardNumber" class="col-form-label">Concession Card Number</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="concessionCardNumber" name="concessionCardNumber" v-model="pass.concession_card_number" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter a concession card number.
                                </div>
                            </div>
                        </div>

                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="startDate" class="col-form-label">Start Date for Pass</label>
                            </div>
                            <div class="col-auto">
                                <input type="date" id="startDate" name="startDate" v-model="pass.date_start" class="form-control" required :min="startDate()">
                            </div>
                        </div>
                        <div v-if="showAutomaticRenewalOption" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="renewAutomatically" class="col-form-label">Automatically Renew at Expiry?</label>
                            </div>
                            <div class="col-auto">
                                <div class="form-switch">
                                    <input class="form-check-input pl-2 org-form-switch-primary" type="checkbox" id="renewAutomatically" name="renewAutomatically" v-model="pass.renew_automatically">
                                </div>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="vehicleRegistrationNumbersKnown" class="col-form-label">Vehicle Registration Number<span v-if="isHolidayPass">s</span> Known</label>
                            </div>
                            <div class="col-auto">
                                <div class="form-switch">
                                    <input class="form-check-input pl-2 org-form-switch-primary" type="checkbox" id="vehicleRegistrationNumbersKnown" name="vehicleRegistrationNumbersKnown" v-model="vehicleRegistrationNumbersKnown">
                                </div>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass && vehicleRegistrationNumbersKnown" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="vehicleRegistration1" class="col-form-label">Vehicle Registration<span v-if="vehicleInputs>1"> 1</span></label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="vehicleRegistration1" name="vehicleRegistration1" v-model="pass.vehicle_registration_1" class="form-control short-control" required="required" pattern="[a-zA-Z0-9]+" maxlength="9">
                                <div class="invalid-feedback">
                                    Please enter a valid vehicle registration.
                                </div>
                            </div>
                            <div v-if="!isHolidayPass" class="col-auto">
                                <button @click="toggleExtraVehicle" class="btn licensing-btn-primary">{{extraVehicleText}}</button>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass && vehicleRegistrationNumbersKnown && vehicleInputs>1" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="vehicleRegistration2" class="col-form-label">Vehicle Registration 2</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="vehicleRegistration2" name="vehicleRegistration2" v-model="pass.vehicle_registration_2" class="form-control short-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid vehicle registration.
                                </div>
                            </div>
                        </div>
                        <div v-if="showDiscountCodeField" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="discountCode" class="col-form-label">Discount Code</label>
                            </div>
                            <div class="col-auto">
                                <input @keyup="validateDiscountCode" v-model="pass.discount_code" type="text" id="discountCode" name="discountCode" ref="discountCode" class="form-control short-control" :class="{'is-invalid' : discountCodeError}" minlength="8" maxlength="8">
                                <div v-if="!pass.email" class="invalid-feedback">
                                    You must enter your email address in order to validate the discount code.
                                </div>
                                <div class="invalid-feedback">
                                    This discount code is not valid.
                                </div>
                            </div>
                        </div>
                        <div v-if="showVoucherCodeField" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="voucherCode" class="col-form-label">Voucher Code</label>
                            </div>
                            <div class="col-auto">
                                <input @change="validateVoucherCode" @keyup="focusVoucherPin" v-model="pass.voucher_code" type="text" id="voucherCode" name="voucherCode" ref="voucherCode" class="form-control short-control" :class="{'is-invalid' : voucherCodeError}" minlength="8" maxlength="8">
                                <div class="invalid-feedback">
                                    This voucher code is not valid, has expired or does not match the pin.
                                </div>
                            </div>
                        </div>
                        <div v-if="pass.voucher_code.length==8 && validateVoucherCode" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="voucherPin" class="col-form-label">Voucher Pin</label>
                            </div>
                            <div class="col-auto">
                                <input @keyup="validateVoucherPin" v-model="pass.voucher_pin" type="text" id="voucherPin" name="voucherPin" ref="voucherPin" class="form-control pin-control" minlength="6" maxlength="6">
                                <div class="invalid-feedback">
                                    This voucher pin is not valid.
                                </div>
                            </div>
                        </div>
                        <div v-if="passOptions" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="passOption" class="col-form-label">Duration</label>
                            </div>
                            <div class="col-auto">
                                <select v-if="passOptions.length>1" @change="updatePrice" v-model="pass.option_id" ref="passOption" id="passOption" name="passOption" class="form-select" aria-label="Pass Option" required="required">
                                    <option v-for="passOption in passOptions" :value="passOption.id" :key="passOption.id">{{passOption.name}}</option>
                                </select>
                                <input v-else type="text" readonly class="form-control-plaintext" id="staticEmail" :value="pass.option_name">
                            </div>
                        </div>
                        <div v-if="totalPrice" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="price" class="col-form-label">Price</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" readonly class="form-control-plaintext fw-bold" id="price" name="price" :value="'$'+totalPrice">
                            </div>
                        </div>
                        <div v-if="discountCodeDiscount" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Discount Amount
                            </div>
                            <div class="col-auto">
                                <strong class="text-success">-${{ discountCodeDiscount }}</strong>
                            </div>
                        </div>
                        <div v-if="voucherRedemptionAmount" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Voucher Balance
                            </div>
                            <div class="col-auto">
                                <strong class="text-success">${{ voucherBalanceRemaining }}</strong>
                            </div>
                        </div>
                        <div v-if="voucherRedemptionAmount" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Voucher Redemption
                            </div>
                            <div class="col-auto">
                                <strong class="text-success">-${{ voucherRedemptionAmount }}</strong>
                            </div>
                        </div>
                        <div v-if="voucherRedemptionAmount" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Voucher Balance Remaining
                            </div>
                            <div class="col-auto">
                                <strong class="text-success">${{ voucherBalanceRemainingIfUsedForThisPurchase }}</strong>
                            </div>
                        </div>
                        <div v-if="discountCodeDiscount || voucherRedemptionAmount" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Sub Total
                            </div>
                            <div class="col-auto lead">
                                <strong>${{ subTotal }}</strong>
                            </div>
                        </div>
                        <div v-if="isRetailer && retailerGroupsForUser && retailerGroupsForUser.length" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Sold Via
                            </div>
                            <div class="col-auto">
                                <template v-if="retailerGroupsForUser && retailerGroupsForUser.length>1">
                                    <select class="form-select" name="retailer_group_id" v-model="pass.sold_via">
                                        <option v-for="retailerGroup in retailerGroupsForUser" :value="retailerGroup.id">{{ retailerGroup.name }}</option>
                                    </select>
                                </template>
                                <template v-else>
                                    <div class="lead"><span class="badge org-badge-primary fw-bold">{{ retailerGroupsForUser[0].name }}</span></div>
                                </template>
                            </div>
                        </div>
                        <div class="row g-1 mb-2 mt-1">
                            <div class="col-md-4">
                                &nbsp;
                            </div>
                            <div class="col-auto">
                                <button v-if="!isLoading" class="btn licensing-btn-primary px-5" type="submit">Next</button>
                                <BootstrapButtonSpinner v-else class="btn licensing-btn-primary px-5" />
                            </div>
                        </div>
                    </form>
                </div>
            </div>

            <div v-else>
                <BootstrapSpinner isLoading="true" />
            </div>

            <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
                {{ systemErrorMessage }}
            </div>

        </div>
</template>

<script>
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'
import { useStore } from '@/stores/state'

export default {
    name: "PurchasePass",
    props: {
        passTypeId: {
            type: [Number, String]
        }
    },
    data: function () {
        return {
            store: useStore(),
            pass: {
                first_name: '',
                last_name: '',
                email: '',
                confirmEmail: '',
                concession_id: 0,
                date_start: this.startDate(),
                discount_code: '',
                voucher_code: '',
                voucher_pin: '',
                state: 'WA',
                park_group: null,
                park_group_id: null,
            },

            isRetailer: false,

            passType: null,
            passOptions: null,
            passOptionsLength: null,
            passPrice: '',
            parkGroups: [],
            loadingParkGroups: false,
            concessionDiscountPercentage: 0,
            concessions: [],
            retailerGroupsForUser: null,
            confirmEmail: '',
            eligibleForConcession: false,
            vehicleRegistrationNumbersKnown: true,
            extraVehicle: false,
            vehicleInputs: 1,
            extraVehicleText: 'Add a second vehicle',

            discountType: null,
            discountPercentage: 0.00,
            discountCodeDiscount: 0.00,

            voucherBalanceRemaining: 0.00,

            discountCodeError: '',
            voucherCodeError: '',
            voucherPinError: '',
            systemErrorMessage: null,
            noParkForPostcodeError: '',

            isLoading: false,
        };
    },
    components: {
        BootstrapButtonSpinner,
        BootstrapSpinner,
    },
    computed: {
        loaded() {
            return this.passType && this.passOptions && this.concessions;
        },
        showPassTypeDescription() {
            console.log('this.isRetailer = ' + this.isRetailer)
            return this.passType && !this.isRetailer;
        },
        showAutomaticRenewalOption() {
            return this.passType && !this.isRetailer;
        },
        showDiscountCodeField() {
            return !this.isRetailer && this.isEmailValid;
        },
        showVoucherCodeField() {
            console.log('this.totalPriceAfterDiscounts = ' + this.totalPriceAfterDiscounts);
            return (this.isEmailValid && (0.00 < this.totalPriceAfterDiscounts) && !this.isRetailer)
        },
        totalPrice() {
            let totalPrice = 0.00;
            if(!this.eligibleForConcession){
                return this.passPrice;
            }
            totalPrice = this.passPrice - ((this.concessionDiscountPercentage / 100) * this.passPrice);
            return totalPrice.toFixed(2);
        },
        totalPriceAfterDiscounts() {
            let totalPriceAfterDiscounts = this.totalPrice - this.discountCodeDiscount;
            return Math.max(totalPriceAfterDiscounts, 0.00).toFixed(2);
        },
        subTotal() {
            let subTotal = this.totalPrice - this.discountCodeDiscount - this.voucherRedemptionAmount;
            return Math.max(subTotal, 0.00).toFixed(2);
        },
        isHolidayPass() {
            if(!this.passType){
                return false;
            }
            return (constants.HOLIDAY_PASS_NAME==this.passType.name ? true : false)
        },
        isAnnualLocalPass() {
            if(!this.passType){
                return false;
            }
            return ('ANNUAL_LOCAL_PASS'==this.passType.name ? true : false)
        },
        isGoldStarPass() {
            if(!this.passType){
                return false;
            }
            return ('GOLD_STAR'==this.passType.name ? true : false)
        },
        indefiniteArticle() {
            return ('A'==this.passType.display_name.substring(0,1) ? 'an' : 'a' )
        },
        showParksList() {
            if(this.pass.park_group){
                const parksInParkGroupName = this.pass.park_group.name.split('/').length;
                if(this.pass.park_group.parks.length > parksInParkGroupName){
                    return true;
                }
            }
            return false;
        },
        isPinjarPass() {
            if(!this.passType){
                return false;
            }
            return ('PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS'==this.passType.name ? true : false)
        },
        isEmailValid() {
            if(this.pass.email && this.confirmEmail){
                if(this.pass.email==this.confirmEmail) {
                    return this.$refs.email.checkValidity() && this.$refs.confirmEmail.checkValidity();
                }
            }
            return false;
        },
        voucherRedemptionAmount() {
            if (0.00>=this.voucherBalanceRemaining) {
                return null;
            }
            if(Number(this.voucherBalanceRemaining) >= this.totalPriceAfterDiscounts){
                return Math.max(this.totalPriceAfterDiscounts, 0.00).toFixed(2);
            } else {
                return Math.max(this.voucherBalanceRemaining, 0.00).toFixed(2);;
            }
        },
        voucherBalanceRemainingIfUsedForThisPurchase() {
            let remaining = this.voucherBalanceRemaining - this.voucherRedemptionAmount;
            return Math.max(remaining, 0.00).toFixed(2);
        },

    },
    methods: {
        startDate: function () {
            let today = new Date();
            return today.toISOString().split('T')[0];
        },
        fetchConcessions: function () {
            let vm = this;
            fetch(apiEndpoints.concessions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.concessions = data.results
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        fetchPassType: function () {
            let vm = this;
            fetch(apiEndpoints.passType(vm.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.passType = data
                vm.$nextTick(() => {
                    if(!vm.pass.email.length){
                        vm.$refs.firstName.focus();
                    } else {
                        vm.$refs.confirmEmail.focus();
                    }
                });
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        fetchPassOptions: function () {
            let vm = this;
            fetch(apiEndpoints.passOptions(vm.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                if(data.results.length > 0) {
                    vm.passOptions = data.results
                    vm.pass.option_id = vm.passOptions[0].id;
                    vm.pass.option_name = vm.passOptions[0].name;
                    vm.passPrice = vm.passOptions[0].price
                } else {
                    this.systemErrorMessage = constants.ERRORS.CRITICAL;
                    console.error(`SYSTEM ERROR: Unable to load options for pass type id: ${vm.passTypeId}`);
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        fetchParkGroups: function () {
            let vm = this;
            vm.loadingParkGroups = true;
            fetch(apiEndpoints.parkGroupsForPostcode(vm.pass.postcode))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }

                if (data.results.length >= 1) {
                    vm.parkGroups = data.results
                    console.log(vm.parkGroups);
                    vm.pass.park_group = Object.assign({}, vm.parkGroups[0]);
                    vm.pass.park_group_id = vm.pass.park_group.id;
                    vm.$nextTick( function() {
                        if(vm.parkGroups.length>1){
                            vm.$refs.parkGroup.focus();
                        }
                    });
                } else {
                    console.log('Something goes here.')
                    vm.noParkForPostcodeError = "Unfortunately there are no local parks for your postcode.";
                    this.$refs.postcode.setCustomValidity("Invalid field.");
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            }).finally(() => (this.loadingParkGroups = false));
        },
        fetchRetailerGroupsForUser: function () {
            let vm = this;
            vm.loading = true;
            fetch(apiEndpoints.retailerGroupsForUser)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                vm.retailerGroupsForUser = data
                if(vm.retailerGroupsForUser && 1==vm.retailerGroupsForUser.length){
                   vm.pass.sold_via =  vm.retailerGroupsForUser[0].id
                }
                console.log(vm.retailerGroupsForUser);
            })
            .catch(error => {
                vm.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            }).finally(() => {
                vm.loading = false;
            });
        },
        updatePrice: function (event) {
            this.passPrice = this.passOptions[event.target.selectedIndex].price
        },
        updateParkGroup: function (event) {
            this.pass.park_group = {...this.parkGroups[event.target.selectedIndex]};
        },
        resetPrice: function () {
            if(!this.eligibleForConcession){
                this.concessionDiscountPercentage = 0.00
                if(this.passOptions.length>1){
                    this.passPrice = this.passOptions[this.$refs.passOption.selectedIndex].price
                } else {
                    this.passPrice = this.passOptions[0].price
                }

            } else {
                console.log('happening');
                this.pass.concession_type = 0;
            }
        },
        updateConcessionDiscount: function (event) {
            if(!this.eligibleForConcession){
                this.concessionDiscountPercentage = 0.00;
            } else {
                if(0==event.target.selectedIndex){
                    this.concessionDiscountPercentage = 0.00;
                } else {
                    this.concessionDiscountPercentage = this.concessions[event.target.selectedIndex-1].discount_percentage
                }
            }
        },
        toggleExtraVehicle: function (e) {
            e.preventDefault();
            this.extraVehicle = !this.extraVehicle;
            if(this.extraVehicle) {
                this.vehicleInputs = 2;
                this.extraVehicleText = 'Remove second vehicle';
            } else {
                this.vehicleInputs = 1;
                this.extraVehicleText = 'Add a second vehicle';
            }
        },
        validateConfirmEmail: function () {
            if(this.confirmEmail!=this.pass.email){
                this.$refs.confirmEmail.setCustomValidity("Invalid field.");
                return false;
            } else {
                this.$refs.confirmEmail.setCustomValidity("");
            }
        },
        validateDiscountCode: function () {

            if(this.pass.discount_code.length && (8!=this.pass.discount_code.length)){
                this.$refs.discountCode.setCustomValidity("Invalid field.");
                this.discountCodeDiscount = 0.00;
                return false;
            } else {
                if(0==this.pass.discount_code.length){
                    this.$refs.discountCode.setCustomValidity("");
                    return true;
                } else {
                    return this.validateDiscountCodeBackend();
                }
            }
        },
        validateVoucherCode: function () {
            console.log('this.pass.voucher_code.length = ' + this.pass.voucher_code.length)
            if(this.pass.voucher_code.length && 8!=this.pass.voucher_code.length){
                console.log('voucher code is invalid')
                this.voucherBalanceRemaining = 0.00;
                this.$refs.voucherCode.setCustomValidity("Invalid field.");
                return false;
            } else {
                console.log('voucher code passes basic validation')
                this.$refs.voucherCode.setCustomValidity("");
                return true;
            }
        },
        validatePostcode: function () {
            /*
                This validation only occurs for local park passes (due to logic in the template)
            */
            let vm = this;
            vm.noParkForPostcodeError = '';
            if(vm.pass.postcode.length==4){
                /*
                const firstNumber = vm.pass.postcode.substring(0,1);
                if('6'==firstNumber){

                } else {
                    vm.$refs.postcode.setCustomValidity("Invalid field.");
                    vm.parkGroups = []
                    vm.pass.park_group = null
                    return false;
                }*/
                fetch(apiEndpoints.isPostcodeValid(vm.pass.postcode))
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error);
                        return Promise.reject(error);
                    }
                    const isPostcodeValid = data.is_postcode_valid
                    console.log('isPostcodeValid = ' + isPostcodeValid)
                    if(!isPostcodeValid){
                        vm.$refs.postcode.setCustomValidity("Invalid field.");
                        vm.parkGroups = []
                        vm.pass.park_group = null
                        return false;
                    }
                    vm.$refs.postcode.setCustomValidity("");
                    vm.fetchParkGroups();
                    return true;
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
                });
            } else {
                vm.$refs.postcode.setCustomValidity("Invalid field.");
                vm.parkGroups = []
                vm.pass.park_group = null
                return false;
            }
        },
        focusVoucherPin: function() {
            if(this.pass.voucher_code.length==8){
                this.$nextTick(() => {
                     this.$refs.voucherPin.focus();
                });
            }
        },
        validateVoucherPin: function () {

            console.log('this.pass.voucher_pin.length = ' + this.pass.voucher_pin.length)
            if(6!=this.pass.voucher_pin.length){
                console.log('Pin is not valid.')
                this.$refs.voucherPin.setCustomValidity("Invalid field.");
                return false;
            } else {
                if(this.pass.voucher_pin.length && !/^\d+$/.test(this.pass.voucher_pin)){
                    this.$refs.voucherPin.setCustomValidity("Invalid field.");
                    return false;
                } else {
                    console.log('Pin is valid.')
                    this.$refs.voucherPin.setCustomValidity("");
                    console.log('calling validateVoucherCodeBackend.')
                    return this.validateVoucherCodeBackend();
                }
            }
        },
        validateDiscountCodeBackend: function () {
            let vm = this;
            fetch(apiEndpoints.isDiscountCodeValid(vm.pass.email, vm.pass.discount_code, vm.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                const isDiscountCodeValid = data.is_discount_code_valid;
                console.log('isDiscountCodeValid = ' + isDiscountCodeValid)
                if(!isDiscountCodeValid){
                    this.$refs.discountCode.setCustomValidity("Invalid field.");
                    this.discountCodeDiscount = 0.00;
                    return false;
                } else {
                    vm.discountType = data.discount_type
                    console.log('vm.discountType = ' + vm.discountType)
                    if('percentage'==vm.discountType) {
                        vm.discountPercentage = data.discount
                        console.log('vm.discountPercentage = ' + vm.discountPercentage)
                        vm.discountCodeDiscount = vm.totalPrice * (vm.discountPercentage/100);
                        vm.discountCodeDiscount = vm.discountCodeDiscount.toFixed(2);
                    } else {
                        vm.discountCodeDiscount = data.discount
                    }
                    console.log('vm.discountCodeDiscount = ' + vm.discountCodeDiscount)
                    // Check if the discount is a percentage or an amount
                    vm.$refs.discountCode.setCustomValidity("");
                    return true;
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        validateVoucherCodeBackend: function () {
            let vm = this;
            fetch(apiEndpoints.isVoucherValid(vm.pass.email, vm.pass.voucher_code, vm.pass.voucher_pin))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                const isVoucherCodeValid = data.is_voucher_code_valid;
                console.log('isVoucherCodeValid = ' + isVoucherCodeValid)
                if(!isVoucherCodeValid){
                    this.voucherBalanceRemaining = 0.00;
                    this.$refs.voucherCode.setCustomValidity("Invalid field.");
                    return false;
                } else {
                    this.voucherBalanceRemaining = data.balance_remaining.toFixed(2);
                    console.log('this.voucherBalanceRemaining = ' + this.voucherBalanceRemaining);
                    this.$refs.voucherCode.setCustomValidity("");
                    return true;
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        validateForm: async function () {
            let vm = this;
            var forms = document.querySelectorAll('.needs-validation')

            console.log("validating form -- >")

            if(vm.isEmailValid){
                console.log("email is valid -- >")
                this.validateConfirmEmail();
                if(!this.isRetailer){
                    this.validateDiscountCode();
                    if(vm.showVoucherCodeField){
                        console.log("vm.showVoucherCodeField -- >")
                        let voucherCodeValid = this.validateVoucherCode();
                        let voucherPinValid = false;
                        if(this.pass.voucher_code.length && voucherCodeValid){
                            console.log("voucherCodeValid valid -- >")
                            voucherPinValid = this.validateVoucherPin();
                        }
                        /* Todo: There are still issues with the validation process.
                        if (typeof voucherPinValid !== 'undefined'){
                            console.log("voucherPinValid is undefined returning false -- >")
                            return false;
                        }*/
                        console.log("voucherPinValid = " + voucherPinValid)
                        if(voucherCodeValid && voucherPinValid){
                            console.log("Is this happening -- >")
                            this.validateVoucherCodeBackend();
                        }
                    }
                }
            }

            Array.prototype.slice.call(forms)
            .forEach(function (form) {
                if(form.checkValidity()){
                    vm.submitForm();
                } else {
                    form.classList.add('was-validated');
                    console.log($(".invalid-feedback:first"));
                    $(".invalid-feedback:visible:first").siblings('input').focus();
                }

            });

            console.log(this.pass);
            return false;
        },
        submitForm: function() {
            let vm = this;
            vm.isLoading = true;
            vm.pass.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            console.log('vm.pass.date_start = ' + vm.pass.date_start);
            if(vm.pass.park_group_id){
               vm.pass.park_group = vm.pass.park_group_id;
            } else {
                vm.pass.park_group = null;
            }

            console.log('vm.pass.park_group = ' + vm.pass.park_group);
            vm.pass.option = vm.pass.option_id;
            vm.pass.pass_type_name = vm.passType.name;
            console.log('vm.pass = ' + JSON.stringify(vm.pass));
            //alert('vm.pass = ' + JSON.stringify(vm.pass));
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pass)
            };
            fetch(apiEndpoints.createPass, requestOptions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                window.location.href = '/cart/';
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
            console.log(this.voucher);
            return false;
        }
    },
    created: function () {
        this.fetchPassType();
        this.fetchConcessions();
        this.fetchPassOptions();
    },
    mounted: function () {
        let vm = this;
        if(vm.store.userData){
            if(vm.store.userData.is_authenticated&&'external'==vm.store.userData.authorisation_level) {
                vm.pass.first_name = vm.store.userData.user.first_name
                vm.pass.last_name = vm.store.userData.user.last_name
                vm.pass.email = vm.store.userData.user.email
            }
            if('retailer'==vm.store.userData.authorisation_level) {
                vm.isRetailer = true;
                vm.fetchRetailerGroupsForUser();
            }
            console.log('vm.isRetailer = ' + vm.isRetailer);
        }
    }
};
</script>

<style scoped>

    .form-control.no-validate:valid {
        border-color: #ced4da;
        padding-right: .75rem;
        background: none;
    }
    .short-control{
        width:180px;
    }
    .pin-control{
        width:120px;
    }
    .parks-list{
        max-width:400px;
        margin:0;
        padding:0;
    }
    .parks-list li {
        list-style-type: none;
        display:inline-flex;
        margin-right:3px;
    }

    .parks-list li span.badge {
        color: #fff;
        background-color: #337ab7;
    }
</style>
