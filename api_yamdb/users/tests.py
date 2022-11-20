from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestUserModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='TestUser',
            email='testuser@yamdb.fake'
        )
        cls.moder = User.objects.create(
            first_name='ModerFirstName',
            last_name='ModerLastNAme',
            username='TestModer',
            bio='About me mafa yo',
            role='moderator',
            email='testmoder@yamdb.fake'
        )
        cls.admin = User.objects.create(
            first_name='AdminFirstName',
            last_name='AdminLastNAme',
            username='TestAdmin',
            role='admin',
            email='testadmin@yamdb.fake'
        )

    def test_correct_roles(self):
        """
        Проверяем отображаемые роли.
        """
        user = TestUserModel.user
        moder = TestUserModel.moder
        admin = TestUserModel.admin
        with self.subTest():
            self.assertEqual(user.role, User.USER)
            self.assertEqual(moder.role, User.MODERATOR)
            self.assertEqual(admin.role, User.ADMIN)
