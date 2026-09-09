from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates the first user/superuser for QuickBook'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email', type=str, default='admin@quickbook.com')
        parser.add_argument('--password', type=str, default='admin123')
        parser.add_argument('--vendor', action='store_true', help='Set user as vendor')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        is_vendor = options['vendor']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists."))
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                is_vendor=is_vendor
            )
            self.stdout.write(self.style.SUCCESS(f"User '{username}' created successfully."))

        self.stdout.write(self.style.SUCCESS(
            f"User Details:\n"
            f"  ID: {user.id}\n"
            f"  Username: {user.username}\n"
            f"  Email: {user.email}\n"
            f"  Referral Code: {user.referral_code}\n"
            f"  Is Staff: {user.is_staff}\n"
            f"  Is Vendor: {user.is_vendor}\n"
        ))
