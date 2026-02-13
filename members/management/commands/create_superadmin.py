from django.core.management.base import BaseCommand
from members.models import customer_sign

class Command(BaseCommand):
    help = 'Create a superadmin user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superadmin')
        parser.add_argument('--email', type=str, help='Email for the superadmin')
        parser.add_argument('--password', type=str, help='Password for the superadmin')
        parser.add_argument('--mobile', type=str, help='Mobile number for the superadmin')

    def handle(self, *args, **options):
        # Get inputs from arguments or prompt user
        username = options.get('username') or input('Enter superadmin username: ')
        email = options.get('email') or input('Enter superadmin email: ')
        password = options.get('password') or input('Enter superadmin password: ')
        mobile = options.get('mobile') or input('Enter superadmin mobile number: ')
        
        # Check if user already exists
        if customer_sign.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email {email} already exists'))
            return
        
        # Create superadmin user
        superadmin = customer_sign.objects.create(
            username=username,
            email=email,
            password=password,
            mobile_number=mobile,
            user_type='customer',
            role='superadmin',
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created superadmin user: {username}'))
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Mobile: {mobile}')
