import math

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from vendor.models import CustomerProfile, Invoice, Receipt, Offer

from vendorpromo.models import CouponCode

User = get_user_model()


class ValidateCodeCheckoutProcessAPIViewTests(TestCase):

    def setUp(self):
        pass

    # def test_post_code_valid(self):
    #     raise NotImplementedError

    # def test_post_code_invalid(self):
    #     raise NotImplementedError


class ValidateLinkCodeAPIView(TestCase):

    def setUp(self):
        pass

    # def test_post_code_valid(self):
    #     raise NotImplementedError

    # def test_post_code_invalid(self):
    #     raise NotImplementedError


class ValidateCouponCodeCheckoutProcessAPIViewTest(TestCase):

    fixtures = ['user', 'unit_test']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)
        self.customer_profile = CustomerProfile.objects.get(pk=1)
        self.existing_invoice = Invoice.objects.get(pk=1)
        self.url = reverse('checkout-validation-coupon-code', kwargs={'invoice_uuid': self.existing_invoice.uuid})

    def test_apply_coupon_percent_off_on_individual_products(self):
        Receipt.objects.filter(pk__gte=0).delete()
        self.existing_invoice.update_totals()
        multiple_products_coupon_percent = CouponCode.objects.get(pk=4)
        should_be_coupon_discount = math.fabs(multiple_products_coupon_percent.promo.applies_to.current_price() * sum([order_item.total for order_item in self.existing_invoice.order_items.all()])) / 100  # Promo code applies to all the products in the invoice
        current_discount = self.existing_invoice.get_discounts()
        current_subtotal = self.existing_invoice.subtotal
        current_total = self.existing_invoice.total

        response = self.client.post(self.url, {'promo_code': multiple_products_coupon_percent.code})

        self.existing_invoice.refresh_from_db()
        self.existing_invoice.update_totals()

        self.assertIn("Promo Code Applied", str(response.content))
        self.assertAlmostEqual(should_be_coupon_discount + current_discount, self.existing_invoice.get_discounts())
        self.assertEquals(current_subtotal, self.existing_invoice.subtotal)
        self.assertNotEquals(current_total, self.existing_invoice.total)
        self.assertEquals(current_subtotal - (should_be_coupon_discount + current_discount), self.existing_invoice.total)

    def test_apply_coupon_fixed_amount_on_individual_products(self):
        Receipt.objects.filter(pk__gte=0).delete()
        self.existing_invoice.update_totals()
        multiple_products_coupon_fixed = CouponCode.objects.get(pk=3)
        should_be_coupon_discount = math.fabs(multiple_products_coupon_fixed.promo.applies_to.current_price() * sum([order_item.quantity for order_item in self.existing_invoice.order_items.all()]))  # Promo code applies to all the products in the invoice
        current_discount = self.existing_invoice.get_discounts()
        current_subtotal = self.existing_invoice.subtotal
        current_total = self.existing_invoice.total
        
        response = self.client.post(self.url, {'promo_code': multiple_products_coupon_fixed.code})
        self.existing_invoice.refresh_from_db()
        self.existing_invoice.update_totals()

        self.assertIn("Promo Code Applied", str(response.content))
        self.assertEquals(should_be_coupon_discount + current_discount, self.existing_invoice.get_discounts())
        self.assertEquals(current_subtotal, self.existing_invoice.subtotal)
        self.assertNotEquals(current_total, self.existing_invoice.total)
        self.assertEquals(current_subtotal - (should_be_coupon_discount + current_discount), self.existing_invoice.total)

    def test_apply_coupon_percent_off_on_invoice(self):
        self.existing_invoice.empty_cart()
        self.existing_invoice.add_offer(Offer.objects.get(pk=6))
        single_product_coupon_percent = CouponCode.objects.get(pk=5)
        self.existing_invoice.update_totals()
        should_be_coupon_discount = math.fabs(single_product_coupon_percent.promo.applies_to.current_price() * sum([order_item.total for order_item in self.existing_invoice.order_items.all()])) / 100  # Promo code applies to all the products in the invoice
        current_discount = self.existing_invoice.get_discounts()
        current_subtotal = self.existing_invoice.subtotal
        current_total = self.existing_invoice.total

        response = self.client.post(self.url, {'promo_code': single_product_coupon_percent.code})

        self.existing_invoice.refresh_from_db()
        self.existing_invoice.update_totals()

        self.assertIn("Promo Code Applied", str(response.content))
        self.assertAlmostEqual(should_be_coupon_discount + current_discount, self.existing_invoice.get_discounts())
        self.assertEquals(current_subtotal, self.existing_invoice.subtotal)
        self.assertNotEquals(current_total, self.existing_invoice.total)
        self.assertEquals(current_subtotal - (should_be_coupon_discount + current_discount), self.existing_invoice.total)
    
    def test_apply_coupon_fixed_amount_on_invoice(self):
        self.existing_invoice.empty_cart()
        self.existing_invoice.add_offer(Offer.objects.get(pk=6))
        single_product_coupon_fixed = CouponCode.objects.get(pk=6)
        should_be_coupon_discount = math.fabs(single_product_coupon_fixed.promo.applies_to.current_price() * sum([order_item.quantity for order_item in self.existing_invoice.order_items.all()]))  # Promo code applies to all the products in the invoice
        current_discount = self.existing_invoice.get_discounts()
        current_subtotal = self.existing_invoice.subtotal
        current_total = self.existing_invoice.total

        response = self.client.post(self.url, {'promo_code': single_product_coupon_fixed.code})

        self.existing_invoice.refresh_from_db()
        self.existing_invoice.update_totals()

        self.assertIn("Promo Code Applied", str(response.content))
        self.assertEquals(should_be_coupon_discount + current_discount, self.existing_invoice.get_discounts())
        self.assertEquals(current_subtotal, self.existing_invoice.subtotal)
        self.assertNotEquals(current_total, self.existing_invoice.total)
        self.assertEquals(current_subtotal - (should_be_coupon_discount + current_discount), self.existing_invoice.total)
    
    def test_return_invalid_code(self):
        invalid_code = "invalid_code"

        response = self.client.post(self.url, {'promo_code': invalid_code})

        self.assertIn("Invalid Code", str(response.content))
    
    # Need to update to add a coupon without a previously owned product
    # def test_return_one_coupon_per_checkout(self):
    #     multiple_products_coupon_percent = CouponCode.objects.get(pk=4)
    #     multiple_products_coupon_fixed = CouponCode.objects.get(pk=3)

    #     response = self.client.post(self.url, {'promo_code': multiple_products_coupon_percent.code})
    #     response = self.client.post(self.url, {'promo_code': multiple_products_coupon_fixed.code})

    #     self.assertIn("You can only apply one promo code per checkout session", str(response.content))

    def test_return_invalid_code_on_product_in_cart(self):
        single_product_coupon_fixed = CouponCode.objects.get(pk=5)

        response = self.client.post(self.url, {'promo_code': single_product_coupon_fixed.code})

        self.assertIn("Code does not apply to any of the products in you cart", str(response.content))
