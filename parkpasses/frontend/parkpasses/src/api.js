
module.exports = {

    /* ========================= User Data =============================================*/

    userData:                           '/api/users/user-data/?format=json',
    select2Customers:                   '/api/users/users/get_customers',
    allUsers:                           '/api/users/users/',

    /* ========================= Concessions ============================================*/

    concessions:                        '/api/concessions/concessions/?format=json',
    concession: function (id) {
        return                          `/api/concessions/concessions/${id}/?format=json`;
    },

    /* ========================= Passes =================================================*/

    passesList:                         '/api/passes/internal/passes/',
    passesListExternal:                 '/api/passes/external/passes/',
    retailerPassesList:                 '/api/passes/retailer/passes/',
    internalPass: function (passId) {
        return                          `/api/passes/internal/passes/${passId}`
    },

    passProcessingStatusesDistinct:     '/api/passes/pass-processing-statuses-distinct?format=json',
    createPass:                         '/api/passes/external/passes/',
    updatePass: function (id) {
        return                          `/api/passes/internal/passes/${id}/`;
    },
    updatePassExternal: function (id) {
        return                          `/api/passes/external/passes/${id}/`;
    },
    internalParkPassPdf: function (passId) {
        return                          `/api/passes/internal/passes/${passId}/retrieve-park-pass-pdf`
    },
    externalParkPassPdf: function (passId) {
        return                          `/api/passes/external/passes/${passId}/retrieve-park-pass-pdf`
    },
    retailerParkPassPdf: function (passId) {
        return                          `/api/passes/retailer/passes/${passId}/retrieve-park-pass-pdf`
    },

    /* ========================= Pass Types =============================================*/

    passTypesDistinct:                  '/api/passes/pass-types-distinct?format=json',
    passTypes:                          '/api/passes/pass-types?format=json',
    passType: function (id) {
        return                          `/api/passes/pass-types/${id}/?format=json`;
    },

    /* ========================= Pass Options ===========================================*/

    passOptions: function (passTypeId) {
        return                          `/api/passes/pass-options-by-pass-type-id?pass_type_id=${passTypeId}`;
    },
    defaultPassOptions: function (passTypeId) {
        return                          `/api/passes/default-pass-options-by-pass-type-id?pass_type_id=${passTypeId}`;
    },

    /* ========================= Discount Codes =========================================*/
    discountCodeBatchPaginatedList:     '/api/discount-codes/internal/discount-code-batches/',
    discountCodeBatch: function (id) {
        return                          `/api/discount-codes/internal/discount-code-batches/${id}/`;
    },
    updateDiscountCodeBatch: function (id) {
        return                          `/api/discount-codes/internal/discount-code-batches/${id}/`;
    },
    createDiscountCodeBatch:             '/api/discount-codes/internal/discount-code-batches/',
    isDiscountCodeValid: function (email, code, pass_type_id) {
        return                          `/api/discount-codes/validate-discount-code?email=${email}&code=${code}&pass_type_id=${pass_type_id}`;
    },
    discountCodesXlsx: function (discount_code_batch_id) {
        return                          `/api/discount-codes/internal/discount-codes-xlsx/${discount_code_batch_id}/`;
    },

    /* ========================= Vouchers ===============================================*/
    vouchersInternalPaginatedList:      '/api/vouchers/internal/vouchers/',
    isVoucherValid: function (email, code, pin) {
        return                          `/api/vouchers/validate-voucher?email=${email}&code=${code}&pin=${pin}`;
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

    cart:                               '/api/cart/cart/?format=json',
    deleteCartItem: function (id) {
        return                          `/api/cart/cart-items/${id}/`;
    },

    /* ========================= Pricing Windows ========================================*/

    pricingWindowsPaginatedList:        '/api/passes/internal/pricing-windows/',
    savePricingWindow:                  '/api/passes/internal/pricing-windows/',
    deletePricingWindow: function (id) {
        return                          `/api/passes/internal/pricing-windows/${id}/`;
    },

    /* ========================= FAQs ===================================================*/

    faqsList:                           '/api/help/faqs/',

    /* ========================= Help ===================================================*/

    helpDetailByLabel: function (label) {
        return                          `/api/help/help-detail/${label}/`;
    },

    /* ========================= Orders =================================================*/

    ordersListExternal:                 '/api/orders/external/orders',
    orderRetrieveExternal: function (uuid) {
        return                          `/api/orders/external/order-by-uuid/${uuid}/`;
    },

    /* ========================= Org Model Documents ====================================*/

    uploadOrgModelDocuments:            '/api/org-model-documents/upload-documents',

    /* ========================= Org Model Logs ====================================*/

    userActionLog: function (appLabel, model, object_id) {
        return                          `/api/org-model-logs/user-actions?app_label=${appLabel}&model=${model}&object_id=${object_id}&format=datatables`;
    }
}
