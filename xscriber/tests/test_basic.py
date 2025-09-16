from django.test import TestCase, Client
from django.urls import reverse


class BasicViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse('xscriber:index'))
        self.assertEqual(response.status_code, 200)

    def test_project_list_api(self):
        response = self.client.get(reverse('xscriber:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.json())

    def test_create_project_api(self):
        data = {'name': 'Test Project', 'description': 'Test Description'}
        response = self.client.post(
            reverse('xscriber:create_project'),
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('project_id', response.json())