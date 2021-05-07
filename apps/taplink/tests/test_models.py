from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.taplink.models import Deck
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import ImageFieldFile


User = get_user_model()


class TaplinkDeckTests(TestCase):
    
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
        
        self.deck = Deck.objects.create(
            user = self.user,
            slug = 'random_string',
            icon = SimpleUploadedFile("taplink_image.jpg", content=b'', content_type="image/jpg"),
            body = 'random_body_string',
            whatsapp = 'https://wa.me/+996703914165',
            telegram = 'https://telegram.me/usernickname',
            )

    def test_deck_created(self):
        self.assertEqual(self.deck.user, self.user)
        self.assertEqual(self.deck.slug, 'random_string')
        self.assertEqual(self.deck.body, 'random_body_string')
        self.assertEqual(self.deck.whatsapp, 'https://wa.me/+996703914165')
        self.assertEqual(self.deck.telegram, 'https://telegram.me/usernickname')

    def test_whatsapp_max_length(self):
        max_length = self.deck._meta.get_field('whatsapp').max_length
        self.assertEquals(max_length, 255)
    
    def test_telegram_max_length(self):
        max_length = self.deck._meta.get_field('telegram').max_length
        self.assertEquals(max_length, 255)

    def test_get_absolute_url(self):
        self.assertEquals(self.deck.get_absolute_url(), f'/taplink/deck_page/{self.deck.slug}/')
