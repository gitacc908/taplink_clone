from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.store.models import Category, Product
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


class TestCategoriesModel(TestCase):
    
    def setUp(self):
        """"
        setUp: Run once for every test method to setup clean data."
        """
        self.user = User.objects.create_user(
            phone_number="+996703908070",
            first_name="myuserfirstname",
            last_name="myuserlastname",
            password="Testpass123",
        )

        self.category = Category.objects.create(
            owner=self.user, 
            title='pumpkins',
        )

    def test_category_model_entry(self):
        """
        Test Category model data insertion/types/field attributes
        """
        self.assertTrue(isinstance(self.category, Category))
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(self.category.title, 'pumpkins')


class TestProductsModel(TestCase):
    
    def setUp(self):
        """"
        setUp: Run once for every test method to setup clean data."
        """
        self.user = User.objects.create_user(
            phone_number="+996703908070",
            first_name="myuserfirstname",
            last_name="myuserlastname",
            password="Testpass123",
        )
        self.category = Category.objects.create(
            owner=self.user, 
            title='pumpkins',
        )
        self.product = Product.objects.create(
            owner=self.user, 
            title='product title',
            category=self.category,
            main_image=SimpleUploadedFile("product_image.jpg", content=b'', 
                                                content_type="image/jpg"),
            desctiption='some description',
            price=100,
            discount=20,
            slug='someuniqueslug',
        )

    def test_product_model_entry(self):
        """
        Test Product model data insertion/types/field attributes
        """
        self.assertTrue(isinstance(self.product, Product))
        self.assertEqual(self.product.title, 'product title')
        self.assertEqual(self.product.desctiption, 'some description')
        self.assertEqual(self.product.category, self.category)

# TODO: MORE TESTS NEEDED XD.
