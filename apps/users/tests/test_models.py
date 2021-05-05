from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class CustomUserTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData: Run once to set up non-modified data for all class methods.
        """
        cls.user = User.objects.create_user(
            phone_number = "+996703908070",
            first_name = "myuserfirstname",
            last_name = "myuserlastname",
            password="Testpass123"
        )
        cls.superuser = User.objects.create_superuser(
            phone_number = "+99703102030",
            password = "adminpassword"
        )

    def test_create_user(self):

        self.assertEqual(self.user.phone_number, "+996703908070")
        self.assertEqual(self.user.first_name, "myuserfirstname")
        self.assertEqual(self.user.last_name, "myuserlastname")
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_create_superuser(self):
        
        self.assertEqual(self.superuser.phone_number, "+99703102030")
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    def test_first_name_label(self):
        field_label = self.user._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label,'first_name')

    def test_first_name_max_length(self):
        max_length = self.user._meta.get_field('first_name').max_length
        self.assertEquals(max_length,255)

    def test_object_name_is_last_name_comma_first_name(self):
        expected_object_name = '%s, %s' % (self.user.last_name, self.user.first_name)
        self.assertEquals(expected_object_name, self.user.get_full_name())

    def test_get_absolute_url(self):
        self.assertEquals(self.user.get_absolute_url(),'/profile/1/')
