from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.inventory.models import ProductVariant
from .models import Customer, Order, OrderItem


class OrdersWorkflowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Ensure groups exist for permission checks
        self.sales_group, _ = Group.objects.get_or_create(name='Sales')

        # Create sales user and login
        self.sales_user = User.objects.create(
            phone_number='081234567890',
            first_name='Sales',
            last_name='User',
            is_active=True,
        )
        self.sales_user.set_password('testpass123')
        self.sales_user.save()
        self.sales_user.groups.add(self.sales_group)

        self.client.force_login(self.sales_user)

        # Create a customer for this sales user
        self.customer = Customer.objects.create(
            name='Toko Test',
            phone_number='081111111111',
            address='Jl. Contoh 123',
            sales_pic=self.sales_user,
        )

        # Create a product variant for order items
        self.variant = ProductVariant.objects.create(
            product_type='SOFT',
            size_grams=1000,
            qty_in_stock=100,
            reserved_stock=0,
            default_price=5000,
        )

    def test_order_create_page_renders_and_contains_fields(self):
        response = self.client.get(reverse('orders:order-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tambah Item')
        self.assertContains(response, 'name="customer"')
        self.assertContains(response, 'name="order_date"')
        self.assertContains(response, 'name="payment_method"')
        self.assertContains(response, 'id="add-item-btn"')
        self.assertContains(response, 'function addItem()')

    def test_can_create_order_and_totals_calculated(self):
        url = reverse('orders:order-create')
        data = {
            'customer': str(self.customer.pk),
            'order_date': '2026-03-10',
            'payment_method': 'CASH',

            # Formset management fields
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '1',
            'items-MAX_NUM_FORMS': '1000',

            # First (and only) item
            'items-0-product_variant': str(self.variant.pk),
            'items-0-quantity': '2',
            'items-0-unit_price': '5000',
        }

        response = self.client.post(url, data, follow=True)
        # Should redirect to order detail page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pesanan ORD-')

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertTrue(order.order_number.startswith('ORD-'))
        self.assertEqual(order.total_price, 10000)

        # Item subtotal should be qty * unit_price
        item = order.items.first()
        self.assertEqual(item.subtotal, 10000)

        # Reserved stock should increase by quantity
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.reserved_stock, 2)

    def test_rejects_zero_quantity(self):
        url = reverse('orders:order-create')
        data = {
            'customer': str(self.customer.pk),
            'order_date': '2026-03-10',
            'payment_method': 'CASH',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '1',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-product_variant': str(self.variant.pk),
            'items-0-quantity': '0',
            'items-0-unit_price': '5000',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jumlah harus minimal 1')
        # Ensure no order was created
        self.assertEqual(Order.objects.count(), 0)

    def test_order_list_search_and_sales_scope(self):
        # Create a second sales user and order to validate scope
        User = get_user_model()
        other_sales = User.objects.create(
            phone_number='081234567891',
            first_name='Other',
            last_name='Sales',
            is_active=True,
        )
        other_sales.set_password('testpass123')
        other_sales.save()
        other_sales.groups.add(self.sales_group)

        order1 = Order.objects.create(
            customer=self.customer,
            who_inputs=self.sales_user,
            payment_method='CASH',
            total_price=5000,
        )
        order2 = Order.objects.create(
            customer=self.customer,
            who_inputs=other_sales,
            payment_method='CASH',
            total_price=2000,
        )

        # Sales should only see their own orders
        response = self.client.get(reverse('orders:order-list'))
        self.assertContains(response, order1.order_number)
        self.assertNotContains(response, order2.order_number)

        # Search by order number should still work
        response = self.client.get(reverse('orders:order-list') + f'?search={order1.order_number}')
        self.assertContains(response, order1.order_number)

    def test_order_detail_and_404(self):
        order = Order.objects.create(
            customer=self.customer,
            who_inputs=self.sales_user,
            payment_method='CASH',
            total_price=1234,
        )
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': order.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)

        # Non-existent order should return 404
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': 999999}))
        self.assertEqual(response.status_code, 404)
