
module.exports = {

    /* ========================= User Data =============================================*/

    userData:                           '/api/users/user-data/',
    select2Customers:                   '/api/users/users/get_customers',
    allUsers:                           '/api/users/users/',

    retailerGroupsForUser:              '/api/retailers/retailer-groups-for-user',

    /* ========================= Concessions ============================================*/

    concessions:                        '/api/concessions/concessions/',
    concession: function (id) {
        return                          `/api/concessions/concessions/${id}/`;
    },

    /* ========================= Passes =================================================*/

    passesList:                         '/api/passes/internal/passes/',
    passesListExternal:                 '/api/passes/external/passes/',
    passesListRetailer:                 '/api/passes/retailer/passes/',
    retrievePassInternal: function (passId) {
        return                          `/api/passes/internal/passes/${passId}`
    },
    retrievePassRetailer: function (passId) {
        return                          `/api/passes/retailer/passes/${passId}`
    },
    passProcessingStatusesDistinct:     '/api/passes/pass-processing-statuses-distinct',
    createPass:                         '/api/passes/external/passes/',
    updatePassInternal: function (id) {
        return                          `/api/passes/internal/passes/${id}/`;
    },
    cancelPass:                         `/api/passes/cancel-pass`,
    proRataRefundPassInternal: function (passId) {
        return                          `/api/passes/internal/passes/${passId}/pro-rata-refund/`
    },
    updatePassExternal: function (id) {
        return                          `/api/passes/external/passes/${id}/`;
    },
    updatePassRetailer: function (id) {
        return                          `/api/passes/retailer/passes/${id}/`;
    },
    internalParkPassPdf: function (passId) {
        return                          `/api/passes/internal/passes/${passId}/retrieve-park-pass-pdf`
    },
    externalParkPassPdf: function (passId) {
        return                          `/api/passes/external/passes/${passId}/retrieve-park-pass-pdf`
    },
    externalParkPassInvoice: function (passId) {
        return                          `/api/passes/external/passes/${passId}/retrieve-invoice`
    },
    retailerParkPassPdf: function (passId) {
        return                          `/api/passes/retailer/passes/${passId}/retrieve-park-pass-pdf`
    },
    internalPassPaymentDetails: function (passId) {
        return                          `/api/passes/internal/passes/${passId}/payment-details`
    },
    checkRacDiscountCode: function (discountHash, email) {
        return                          `/api/passes/check-hash-matches-email/${discountHash}/${email}/`
    },

    /* ========================= Pass Types =============================================*/

    passTypesDistinct:                  '/api/passes/pass-types-distinct/',
    passTypesExternal:                  '/api/passes/external/pass-types/',
    passTypesRetailer:                  '/api/passes/retailer/pass-types/',
    passTypesInternal:                  '/api/passes/internal/pass-types/',
    passTypeExternal: function (passTypeSlug) {
        return                          `/api/passes/external/pass-types/${passTypeSlug}/`;
    },
    passTypeRetailer: function (passTypeSlug) {
        return                          `/api/passes/retailer/pass-types/${passTypeSlug}/`;
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
    internalVoucherInvoice: function (voucherId) {
        return                          `/api/vouchers/internal/vouchers/${voucherId}/retrieve-invoice`
    },
    internalVoucherPaymentDetails: function (voucherId) {
        return                          `/api/vouchers/internal/vouchers/${voucherId}/payment-details`
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

    cart:                               '/api/cart/cart/',
    deleteCartItem: function (id) {
        return                          `/api/cart/cart-items/${id}/`;
    },
    checkout:                           '/ledger-checkout/',

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
    externalOrderInvoice: function (orderId) {
        return                          `/api/orders/external/orders/${orderId}/retrieve-invoice`
    },

    /* ========================= Retailer Groups =========================================*/

    retailerGroupListInternal:          '/api/retailers/internal/retailer-groups/',
    retailerGroupListRetailer:          '/api/retailers/retailer/retailer-groups/',
    activeRetailerGroupListInternal:    '/api/retailers/internal/retailer-groups/active-retailer-groups',
    retailerGroupRetrieveInternal: function (retailerGroupId) {
        `/api/retailers/internal/retailer-groups/${retailerGroupId}/`;
    },
    retailerGroupInviteListInternal:    '/api/retailers/internal/retailer-group-reports/',

    /* ========================= Retailer Group Users =====================================*/

    retailerGroupUserListInternal:      '/api/retailers/internal/retailer-group-users/',
    retailerGroupUserListRetailer:      '/api/retailers/retailer/retailer-group-users/',
    retailerToggleRetailerGroupUserActive: function (retailerGroupUserId) {
        return `/api/retailers/retailer/retailer-group-users/${retailerGroupUserId}/toggle-active/`;
    },
    internalToggleRetailerGroupUserActive: function (retailerGroupUserId) {
        return `/api/retailers/internal/retailer-group-users/${retailerGroupUserId}/toggle-active/`;
    },
    internalToggleRetailerGroupUserIsAdmin: function (retailerGroupUserId) {
        return `/api/retailers/internal/retailer-group-users/${retailerGroupUserId}/toggle-is-admin/`;
    },
    /* ========================= Retailer Group Invites ===================================*/

    retailerGroupInviteListInternal:    '/api/retailers/internal/retailer-group-invites/',
    createRetailerGroupInviteInternal:  '/api/retailers/internal/retailer-group-invites/',
    createRetailerGroupInviteRetailer:  '/api/retailers/retailer/retailer-group-invites/',
    retailerGroupInviteRetrieveExternal: function (uuid) {
        return                          `/api/retailers/external/retailer-group-invites/${uuid}/`;
    },
    resendRetailerGroupInvite: function (id) {
        return                          `/api/retailers/internal/retailer-group-invites/${id}/resend-retailer-group-user-invite/`;
    },
    acceptRetailerGroupInvite: function (uuid) {
        return                          `/api/retailers/external/retailer-group-invites/${uuid}/accept-retailer-group-user-invite/`;
    },
    processRetailerGroupInvite: function (id) {
        return                          `/api/retailers/internal/retailer-group-invites/${id}/process-retailer-group-user-invite/`;
    },

    /* ========================= Reports =================================================*/

    reportsListRetailer:                '/api/reports/retailer/reports',
    reportsListInternal:                '/api/reports/internal/reports',
    reportUpdateInternal:  function (reportId) {
        return                          `/api/reports/internal/reports/${reportId}/`;
    },
    retrieveReportInvoicePdfRetailer:   function (reportId) {
        return                          `/api/reports/retailer/reports/${reportId}/retrieve-invoice-pdf/`;
    },
    retrieveReportInvoicePdfInternal:   function (reportId) {
        return                          `/api/reports/internal/reports/${reportId}/retrieve-invoice-pdf/`;
    },
    retrieveReportPdfRetailer:   function (reportId) {
        return                          `/api/reports/retailer/reports/${reportId}/retrieve-report-pdf/`;
    },
    retrieveReportPdfInternal:   function (reportId) {
        return                          `/api/reports/internal/reports/${reportId}/retrieve-report-pdf/`;
    },

    /* ========================= Org Model Documents ====================================*/

    uploadOrgModelDocuments:            '/api/internal/org-model-documents/upload-documents',
    retrieveOrgModelDocument:  function (documentId) {
        return                          `/api/main/internal/org-model-documents/${documentId}/retrieve-document/`;
    },
    /* ========================= Org Model Logs =========================================*/

    entryTypes:                         '/api/org-model-logs/entry-types',
    listUserActionsLog: function (appLabel, model, objectId) {
        return                          `/api/org-model-logs/user-actions?app_label=${appLabel}&model=${model}&objectId=${objectId}&format=datatables`;
    },
    createCommunicationsLogEntry:       '/api/internal/org-model-logs/communications-log-entries',
    listCommunicationsLogEntries: function (appLabel, model, objectId) {
        return                          `/api/internal/org-model-logs/communications-log-entries?app_label=${appLabel}&model=${model}&objectId=${objectId}&format=datatables`;
    },


}
