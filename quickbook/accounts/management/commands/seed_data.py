from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from events.models import Event
from bookings.models import Booking
from referrals.services import place_user_in_referral_tree

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds realistic sample users, vendors, events, bookings, and binary referral tree into QuickBook database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Flushing existing database tables..."))
        Booking.objects.all().delete()
        Event.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("Seeding realistic QuickBook platform data...")

        # 1. Staff Admin
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@quickbook.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        self.stdout.write(self.style.SUCCESS("Created Admin Staff: admin / admin123"))

        # 2. Vendors with realistic company names
        vendor_data = [
            ('nexus_events', 'contact@nexusevents.com', 'Nexus Events Corp'),
            ('pulse_entertainment', 'info@pulseentertainment.com', 'Pulse Entertainment'),
            ('summit_productions', 'hello@summitproductions.io', 'Summit Productions'),
            ('starlight_media', 'team@starlightmedia.com', 'Starlight Media Group'),
        ]
        vendors = []
        for username, email, company in vendor_data:
            v = User.objects.create_user(
                username=username,
                email=email,
                password='vendor123',
                is_vendor=True
            )
            vendors.append(v)
            self.stdout.write(self.style.SUCCESS(f"Created Vendor: {username} ({company}) / vendor123"))

        # 3. Customer Accounts & Binary Referral Tree
        customer_names = [
            ('alex_morgan', 'alex.morgan@gmail.com'),         # Root user (customer1 replacement)
            ('sarah_connor', 'sarah.connor@yahoo.com'),       # Left of alex_morgan
            ('david_miller', 'david.miller@outlook.com'),     # Right of alex_morgan
            ('emily_watson', 'emily.watson@gmail.com'),       # Left of sarah_connor
            ('michael_brown', 'michael.brown@tech.io'),       # Right of sarah_connor
            ('jessica_taylor', 'jessica.taylor@domain.com'),  # Left of david_miller
            ('daniel_white', 'daniel.white@corp.net'),        # Right of david_miller
            ('sophia_martinez', 'sophia.m@design.co'),       # Left of emily_watson
        ]

        customers = []
        root_user = None

        for idx, (username, email) in enumerate(customer_names):
            user = User.objects.create_user(
                username=username,
                email=email,
                password='customer123'
            )
            if idx == 0:
                root_user = user
                place_user_in_referral_tree(user, None)
            else:
                user.referred_by = root_user
                user.save(update_fields=['referred_by'])
                place_user_in_referral_tree(user, root_user)

            customers.append(user)
            self.stdout.write(self.style.SUCCESS(f"Created Customer: {username} / customer123 (Ref Code: {user.referral_code})"))

        # 4. Create 15 Realistic Events across dates, venues, and vendors
        now = timezone.now()
        sample_events = [
            ("Global AI & Tech Summit 2026", "Annual developer conference covering machine learning, LLMs, and agentic AI systems.", "Silicon Convention Center", now + timedelta(days=5), 150, 140, vendors[0]),
            ("Electric Pulse Music Festival", "Outdoor electronic dance music festival featuring top international DJs and laser shows.", "Grand Skyline Amphitheater", now + timedelta(days=8), 200, 185, vendors[1]),
            ("NextGen Developer Conference", "Deep-dive workshops into modern Web Architecture, Microservices, and Cloud Native DevOps.", "Metropolitan Tech Hub", now + timedelta(days=12), 80, 75, vendors[0]),
            ("Startup Pitch & Venture Gala", "Exclusive networking night connecting seed startups with venture capital investors.", "Grand Hyatt Ballroom", now + timedelta(days=15), 60, 52, vendors[2]),
            ("International Film & Media Expo", "Screenings of indie cinema masterpieces, sound design panels, and director Q&As.", "Starlight Symphony Hall", now + timedelta(days=18), 120, 110, vendors[3]),
            ("UX/UI Design & Product Systems Workshop", "Hands-on masterclass in design tokens, component systems, and user testing.", "Innovation Center Auditorium", now + timedelta(days=22), 45, 40, vendors[0]),
            ("Indie Rock Night Live", "Live acoustic and indie rock performances with local indie band showcases.", "Downtown Arena Stage", now + timedelta(days=25), 100, 92, vendors[1]),
            ("Cloud Architecture & DevOps Masterclass", "Practical sessions on Kubernetes orchestration, CI/CD pipelines, and AWS infra.", "Cyber Hub Center", now + timedelta(days=28), 50, 42, vendors[2]),
            ("Cybersecurity & Zero Trust Forum", "Enterprise security conference covering threat intelligence and data encryption.", "Silicon Convention Center", now + timedelta(days=32), 90, 85, vendors[0]),
            ("Classical Philharmonic Symphony", "A night of classical orchestra masterpieces conducted by maestro Elena Rostova.", "Grand Symphony Hall", now + timedelta(days=35), 150, 135, vendors[3]),
            ("E-Sports Championship Finals 2026", "National tournament finals with live main stage arena gameplay and commentary.", "Metro Dome Gaming Arena", now + timedelta(days=40), 300, 270, vendors[1]),
            ("Sustainable Green Tech & Climate Expo", "Exhibition showcasing solar innovations, EV mobility, and clean energy tech.", "Eco Park Convention Hall", now + timedelta(days=45), 110, 102, vendors[2]),
            ("Fintech & Blockchain Leadership Forum", "Keynotes on decentralized finance, digital banking security, and payment gateways.", "Financial District Tower 1", now + timedelta(days=50), 75, 68, vendors[0]),
            ("Symphonic Jazz & Blues Evening", "Intimate jazz quartet performance featuring smooth brass, piano, and vocal acoustics.", "Blue Note Stage Lounge", now + timedelta(days=55), 40, 34, vendors[3]),
            ("Global Web Development Hackathon", "48-hour continuous coding hackathon with $50k in cash prizes and mentor feedback.", "Tech Campus Auditorium", now + timedelta(days=60), 120, 105, vendors[0]),
        ]

        created_events = []
        for name, desc, venue, date_val, total, avail, v_owner in sample_events:
            e = Event.objects.create(
                name=name,
                description=desc,
                venue=venue,
                event_date=date_val,
                total_seats=total,
                available_seats=avail,
                vendor=v_owner
            )
            created_events.append(e)

        self.stdout.write(self.style.SUCCESS(f"Created {len(created_events)} realistic events!"))

        # 5. Create Sample Ticket Bookings
        sample_bookings = [
            (customers[0], created_events[0], 3, Booking.Status.CONFIRMED), # Alex Morgan -> AI Summit
            (customers[0], created_events[1], 2, Booking.Status.CONFIRMED), # Alex Morgan -> Music Fest
            (customers[1], created_events[0], 2, Booking.Status.CONFIRMED), # Sarah Connor -> AI Summit
            (customers[2], created_events[2], 1, Booking.Status.CONFIRMED), # David Miller -> NextGen Dev
            (customers[3], created_events[3], 4, Booking.Status.CONFIRMED), # Emily Watson -> Startup Gala
            (customers[4], created_events[1], 3, Booking.Status.CANCELLED), # Michael Brown -> Music Fest (Cancelled)
        ]

        for user, event, qty, b_status in sample_bookings:
            Booking.objects.create(
                user=user,
                event=event,
                quantity=qty,
                status=b_status
            )

        self.stdout.write(self.style.SUCCESS("Created sample booking history."))

        self.stdout.write(self.style.SUCCESS("\n========================================================"))
        self.stdout.write(self.style.SUCCESS("        QUICKBOOK REALISTIC SEEDED CREDENTIALS          "))
        self.stdout.write(self.style.SUCCESS("========================================================"))
        self.stdout.write(f"1. STAFF ADMIN:\n   Username: admin | Password: admin123\n")
        self.stdout.write(f"2. VENDORS (Password: vendor123):\n   - nexus_events\n   - pulse_entertainment\n   - summit_productions\n   - starlight_media\n")
        self.stdout.write(f"3. CUSTOMERS (Password: customer123):\n   - alex_morgan (Binary Root, Ref Code: {root_user.referral_code})\n   - sarah_connor\n   - david_miller\n   - emily_watson\n   - michael_brown\n========================================================\n")
