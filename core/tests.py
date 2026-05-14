import shutil
import tempfile

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.test import override_settings

from .models import (
    Assignment,
    EmergencyRequest,
    EmergencyType,
    Requester,
    ResponseTeam,
)


class EmergencyRequestFormTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.user = User.objects.create_user(username='dispatcher', password='secret-pass-123')
        self.client.force_login(self.user)
        self.fire_type = EmergencyType.objects.get(name='Fire')

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def image_file(self, name):
        image_bytes = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'D\x01\x00;'
        )
        return SimpleUploadedFile(name, image_bytes, content_type='image/gif')

    def test_create_request_rejects_invalid_phone(self):
        response = self.client.post(reverse('create_request'), {
            'requester-name': 'John Doe',
            'requester-phone': 'abc',
            'requester-location': 'Main street',
            'request-title': 'Fire',
            'request-description': 'There is smoke in the kitchen.',
            'request-location': 'Kitchen block',
            'request-emergency_type': self.fire_type.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid phone number')
        self.assertEqual(Requester.objects.count(), 0)
        self.assertEqual(EmergencyRequest.objects.count(), 0)

    def test_create_request_accepts_valid_data(self):
        response = self.client.post(reverse('create_request'), {
            'requester-name': 'John Doe',
            'requester-phone': '+216 12 345 678',
            'requester-location': 'Main street',
            'request-title': 'Fire',
            'request-description': 'There is smoke in the kitchen.',
            'request-location': 'Kitchen block',
            'request-emergency_type': self.fire_type.id,
        })

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Requester.objects.count(), 1)
        self.assertEqual(EmergencyRequest.objects.count(), 1)
        self.assertEqual(EmergencyRequest.objects.get().emergency_type, self.fire_type)

    def test_create_request_accepts_before_after_images(self):
        response = self.client.post(reverse('create_request'), {
            'requester-name': 'John Doe',
            'requester-phone': '+216 12 345 678',
            'requester-location': 'Main street',
            'request-title': 'Fire',
            'request-description': 'There is smoke in the kitchen.',
            'request-location': 'Kitchen block',
            'request-emergency_type': self.fire_type.id,
            'request-before_image': self.image_file('before.gif'),
            'request-after_image': self.image_file('after.gif'),
        })
        emergency_request = EmergencyRequest.objects.get()

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(emergency_request.before_image.name.startswith('emergency_requests/before/'))
        self.assertTrue(emergency_request.after_image.name.startswith('emergency_requests/after/'))

    def test_create_request_reuses_same_requester_identity(self):
        requester_data = {
            'requester-name': 'John Doe',
            'requester-phone': '+216 12 345 678',
            'requester-location': 'Main street',
            'request-emergency_type': self.fire_type.id,
            'request-location': 'Kitchen block',
        }

        first_response = self.client.post(reverse('create_request'), {
            **requester_data,
            'request-title': 'Kitchen Fire',
            'request-description': 'There is smoke in the kitchen.',
        })
        second_response = self.client.post(reverse('create_request'), {
            **requester_data,
            'request-title': 'Storage Fire',
            'request-description': 'There is smoke in the storage room.',
        })

        self.assertRedirects(first_response, reverse('home'))
        self.assertRedirects(second_response, reverse('home'))
        self.assertEqual(Requester.objects.count(), 1)
        self.assertEqual(EmergencyRequest.objects.count(), 2)
        self.assertEqual(
            EmergencyRequest.objects.values_list('requester_id', flat=True).distinct().count(),
            1,
        )

    def test_update_request_rejects_short_description(self):
        requester = Requester.objects.create(
            name='John Doe',
            phone='+216 12 345 678',
            location='Main street',
        )
        emergency_request = EmergencyRequest.objects.create(
            requester=requester,
            title='Fire',
            description='There is smoke in the kitchen.',
            location='Kitchen block',
            emergency_type=self.fire_type,
        )

        response = self.client.post(reverse('update_request', args=[emergency_request.id]), {
            'title': 'Fire',
            'description': 'short',
            'location': 'Kitchen block',
            'emergency_type': self.fire_type.id,
            'status': 'resolved',
        })

        emergency_request.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Description must contain at least 10 characters')
        self.assertEqual(emergency_request.status, 'pending')


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dispatcher', password='secret-pass-123')

    def test_home_requires_login(self):
        response = self.client.get(reverse('home'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_login_accepts_valid_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'dispatcher',
            'password': 'secret-pass-123',
        })

        self.assertRedirects(response, reverse('home'))

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))


class DashboardSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dispatcher', password='secret-pass-123')
        self.client.force_login(self.user)

        self.medical_type = EmergencyType.objects.get(name='Medical')
        self.fire_type = EmergencyType.objects.get(name='Fire')
        self.police_type = EmergencyType.objects.get(name='Police')

        medical_requester = Requester.objects.create(
            name='Alice Morgan',
            phone='+216 11 111 111',
            location='North Clinic',
        )
        fire_requester = Requester.objects.create(
            name='Karim Ben Ali',
            phone='+216 22 222 222',
            location='Central Market',
        )
        police_requester = Requester.objects.create(
            name='Maya Stone',
            phone='+216 33 333 333',
            location='Harbor Road',
        )

        EmergencyRequest.objects.create(
            requester=medical_requester,
            title='Medical Kit Needed',
            description='A patient needs urgent support at the clinic.',
            location='North Clinic Room 2',
            emergency_type=self.medical_type,
        )
        EmergencyRequest.objects.create(
            requester=fire_requester,
            title='Kitchen Fire',
            description='A restaurant kitchen has heavy smoke.',
            location='Central Market Kitchen',
            emergency_type=self.fire_type,
            status='in_progress',
        )
        EmergencyRequest.objects.create(
            requester=police_requester,
            title='Road Block',
            description='A blocked road needs police assistance.',
            location='Harbor Road Gate',
            emergency_type=self.police_type,
            status='resolved',
        )

    def test_search_by_title(self):
        response = self.client.get(reverse('home'), {'title': 'Kitchen'})

        self.assertContains(response, 'Kitchen Fire')
        self.assertNotContains(response, 'Medical Kit Needed')
        self.assertNotContains(response, 'Road Block')

    def test_search_by_type(self):
        response = self.client.get(reverse('home'), {'type': str(self.medical_type.id)})

        self.assertContains(response, 'Medical Kit Needed')
        self.assertNotContains(response, 'Kitchen Fire')
        self.assertNotContains(response, 'Road Block')

    def test_search_by_location(self):
        response = self.client.get(reverse('home'), {'location': 'Harbor'})

        self.assertContains(response, 'Road Block')
        self.assertNotContains(response, 'Medical Kit Needed')
        self.assertNotContains(response, 'Kitchen Fire')

    def test_search_requester_by_name(self):
        response = self.client.get(reverse('home'), {'requester': 'Karim'})

        self.assertContains(response, 'Kitchen Fire')
        self.assertContains(response, 'Karim Ben Ali')
        self.assertNotContains(response, 'Medical Kit Needed')
        self.assertNotContains(response, 'Road Block')

    def test_filter_by_status(self):
        response = self.client.get(reverse('home'), {'status': 'in_progress'})

        self.assertContains(response, 'Kitchen Fire')
        self.assertNotContains(response, 'Medical Kit Needed')
        self.assertNotContains(response, 'Road Block')

    def test_all_statuses_shows_every_status(self):
        response = self.client.get(reverse('home'), {'status': ''})

        self.assertContains(response, 'Medical Kit Needed')
        self.assertContains(response, 'Kitchen Fire')
        self.assertContains(response, 'Road Block')


class DashboardPaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dispatcher', password='secret-pass-123')
        self.client.force_login(self.user)
        self.medical_type = EmergencyType.objects.get(name='Medical')
        self.requester = Requester.objects.create(
            name='Nadia Salem',
            phone='+216 44 444 444',
            location='North Station',
        )

        for index in range(7):
            EmergencyRequest.objects.create(
                requester=self.requester,
                title=f'Paged Emergency {index + 1}',
                description='This emergency request is used for pagination tests.',
                location='North Station',
                emergency_type=self.medical_type,
            )

    def test_dashboard_paginates_results(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.context['page_obj'].paginator.per_page, 5)
        self.assertEqual(response.context['page_obj'].paginator.count, 7)
        self.assertEqual(len(response.context['requests']), 5)
        self.assertContains(response, 'Showing 1-5 of 7')

    def test_dashboard_pagination_preserves_search_filters(self):
        response = self.client.get(reverse('home'), {'title': 'Paged', 'status': 'pending', 'page': 2})

        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertEqual(response.context['pagination_query'], 'title=Paged&status=pending')
        self.assertEqual(len(response.context['requests']), 2)


class AdminRegistrationTests(TestCase):
    def test_professional_models_are_registered_in_admin(self):
        for model in [Requester, EmergencyType, EmergencyRequest, ResponseTeam, Assignment]:
            self.assertIn(model, admin.site._registry)


class ManagementCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dispatcher', password='secret-pass-123')
        self.client.force_login(self.user)
        self.medical_type = EmergencyType.objects.get(name='Medical')
        self.requester = Requester.objects.create(
            name='Nadia Salem',
            phone='+216 44 444 444',
            location='North Station',
        )
        self.emergency_request = EmergencyRequest.objects.create(
            requester=self.requester,
            title='Medical Support',
            description='Patient needs medical support at the north station.',
            location='North Station',
            emergency_type=self.medical_type,
        )

    def test_management_list_pages_render(self):
        urls = [
            'requester_list',
            'emergency_type_list',
            'response_team_list',
            'assignment_list',
        ]

        for url_name in urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_response_team_crud_flow(self):
        create_response = self.client.post(reverse('response_team_create'), {
            'name': 'Alpha Team',
            'contact': '+216 55 555 555',
        })
        team = ResponseTeam.objects.get(name='Alpha Team')

        self.assertRedirects(create_response, reverse('response_team_list'))

        update_response = self.client.post(reverse('response_team_update', args=[team.id]), {
            'name': 'Alpha Rescue Team',
            'contact': '+216 55 555 555',
        })
        team.refresh_from_db()

        self.assertRedirects(update_response, reverse('response_team_list'))
        self.assertEqual(team.name, 'Alpha Rescue Team')

        delete_response = self.client.post(reverse('response_team_delete', args=[team.id]))

        self.assertRedirects(delete_response, reverse('response_team_list'))
        self.assertFalse(ResponseTeam.objects.filter(id=team.id).exists())

    def test_assignment_create_page_creates_assignment(self):
        team = ResponseTeam.objects.create(name='Bravo Team', contact='+216 66 666 666')

        response = self.client.post(reverse('assignment_create'), {
            'emergency_request': self.emergency_request.id,
            'response_team': team.id,
        })

        self.assertRedirects(response, reverse('assignment_list'))
        self.assertEqual(Assignment.objects.count(), 1)

    def test_requester_manual_create_rejects_duplicate_identity(self):
        response = self.client.post(reverse('requester_create'), {
            'name': self.requester.name,
            'phone': self.requester.phone,
            'location': self.requester.location,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A requester with the same name, phone, and location already exists.')
        self.assertEqual(Requester.objects.count(), 1)
