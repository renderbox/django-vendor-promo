from vendorpromo.models import Promo


#############
# BASE CLASS
class PromoProcessorBase(object):

    promo = None
    invoice = None
    redeemed = False

    response = None
    response_content = None
    response_error = None
    response_message = None
    is_request_success = False

    def __init__(self, invoice=None):
        if invoice is not None:
            self.invoice = invoice

    ################
    # Promotion Management
    def clear_response_variables(self):
        self.response = None
        self.response_content = None
        self.response_error = None
        self.response_message = None
        self.is_request_success = False

    ################
    # Promotion Management
    def create_promo(self, promo_form):
        '''
        Override if you need to do additional steps when creating a Promo instance,
        such as creating the promo code in an external service if needed.
        '''
        promo = promo_form.save(commit=False)
        promo.save()

    def update_promo(self, promo_form):
        '''
        Override if you need to do additional steps when updating a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        promo = promo_form.save(commit=False)
        promo.save()

    def delete_promo(self, promo):
        '''
        Override if you need to do additional steps when deleting a Promo instance,
        such as editing the promo code in an external service if needed.
        '''
        Promo.delete(promo)

    ################
    # Processor Functions
    def is_code_valid(self, code):
        """
        Overwrite funtion to call external promo services.
        Eg. call Vouchary.io API to see if the code entered is valid.
        """
        raise NotImplementedError

    def redeem_code(self, code):
        """
        Overwrite funtion to call external promo services to redeem code.
        Eg. call Vouchary.io API to redeem the code.
        """
        raise NotImplementedError

    def confirm_redeemed_code(self, code):
        """
        Overwrite funtion to call external promo services to confirm
        that the redeem code was applied.
        Eg. call Vouchary.io API to confirm redeem the code was applied.
        """
        raise NotImplementedError

    def process_promo(self, offer, promo_code):
        '''
        Function used to check if the promo code is valid through external
        promo services such as Vouchery.io. If the code is valid it will
        redeem it.
        NOTE: after purchase, one should confirm that the code
        was applied to an invoice.
        '''
        if not self.is_code_valid(promo_code):
            return None
        self.redeem_code(promo_code)
