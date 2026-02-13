from django.core.management.base import BaseCommand
from members.models import customer_sign

class Command(BaseCommand):
    help = 'Update user types in database'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email of user to update')
        parser.add_argument('--user_type', type=str, help='New user type (customer/seller)')
        parser.add_argument('--role', type=str, help='New role (admin/user/moderator)')
        parser.add_argument('--list', action='store_true', help='List all users')

    def handle(self, *args, **options):
        if options['list']:
            # List all users
            users = customer_sign.objects.all()
            self.stdout.write(self.style.SUCCESS('All Users:'))
            for user in users:
                self.stdout.write(f"  ID: {user.id} | Email: {user.email} | Type: {user.user_type} | Role: {user.role}")
        
        elif options['email'] and (options['user_type'] or options['role']):
            # Update specific user
            email = options['email']
            try:
                user = customer_sign.objects.get(email=email)
                
                if options['user_type']:
                    user.user_type = options['user_type']
                if options['role']:
                    user.role = options['role']
                
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Updated user: {email}'))
                self.stdout.write(f"  Type: {user.user_type} | Role: {user.role}")
            except customer_sign.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ User not found: {email}'))
        else:
            self.stdout.write(self.style.WARNING('Usage:'))
            self.stdout.write('  python manage.py update_users --list')
            self.stdout.write('  python manage.py update_users --email user@email.com --user_type customer --role admin')
            self.stdout.write('  python manage.py update_users --email user@email.com --user_type seller')
