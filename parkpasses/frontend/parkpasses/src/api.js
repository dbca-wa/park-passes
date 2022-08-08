
module.exports = {

    /* ========================= User Data =============================================*/

    userData:                           '/api/users/user-data/?format=json',

    /* ========================= Concessions ============================================*/

    concessions:                        '/api/concessions/concessions/?format=json',
    concession: function (id) {
        return                          `/api/concessions/concessions/${id}/?format=json`;
    },

    /* ========================= Passes =================================================*/

    passesPaginatedList:                '/api/passes/internal/passes/',
    retailerPassesList:                 '/api/passes/retailer/passes/',
    internalPass: function (passId) {
        return                          `/api/passes/internal/passes/${passId}`
    },
    passProcessingStatusesDistinct:     '/api/passes/pass-processing-statuses-distinct?format=json',
    createPass:                         '/api/passes/external/passes/',

    /* ========================= Pass Types =============================================*/

    passTypesDistinct:                  '/api/passes/pass-types-distinct?format=json',
    passTypes:                          '/api/passes/pass-types?format=json',
    passType: function (id) {
        return                          `/api/passes/pass-types/${id}/?format=json`;
    },

    /* ========================= Pass Options ===========================================*/

    passOptions: function (id) {
        return                          `/api/passes/pass-options-by-pass-type-id?pass_type_id=${id}`;
    },

    /* ========================= Discount Codes =========================================*/
    discountCodeBatchPaginatedList:     '/api/discount-codes/internal/discount-code-batches/',
    isDiscountCodeValid: function (id) {
        return                          `to be implimented`;
    },

    /* ========================= Vouchers ===============================================*/
    vouchersInternalPaginatedList:      '/api/vouchers/internal/vouchers/',
    isVoucherValid: function (recipient_email, code, pin) {
        return                          `/api/vouchers/validate-voucher?recipient_email=${recipient_email}&code=${code}&pin=${pin}`;
    },
    saveVoucher:                        '/api/vouchers/external/vouchers/',

    /* ========================= Postcodes ===============================================*/
    isPostcodeValid: function (postcode) {
        return                          `/api/parks/validate-postcode?postcode=${postcode}`;
    },
    parkGroupsForPostcode: function (postcode) {
        return                          `/api/parks/park-groups-for-postcode?postcode=${postcode}`;
    },

    /* ========================= Cart Items =============================================*/

    checkout:                           '/api/cart/checkout/?format=json',


    /* ========================= Pricing Windows ========================================*/

    pricingWindowsPaginatedList:        '/api/passes/internal/pricing-windows/',
    savePricingWindow:                  '/api/passes/internal/pricing-windows/',
    deletePricingWindow: function (id) {
        return                          `/api/passes/internal/pricing-windows/${id}/`;
    },
}
