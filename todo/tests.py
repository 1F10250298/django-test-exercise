from django.test import TestCase, Client
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import os
from todo.models import Task


# Create your tests here.
class SampleTestCase(TestCase):
    def test_sample1(self):
        self.assertEqual(1 + 2, 3)


class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        task = Task(title='task1', due_at=due)
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task1')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, due)

    def test_create_task2(self):
        task = Task(title='task2')
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task2')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, None)

    def test_create_task_empty_title_sets_default(self):
        task = Task(title='')
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, '無題のタスク')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, None)

    def test_is_overdue_future(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()

        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task2', due_at=due)
        task.save()

        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        due = None
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task3', due_at=due)
        task.save()

        self.assertFalse(task.is_overdue(current))


class TodoViewTestCase(TestCase):
    def test_index_get(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_post(self):
        client = Client()
        data = {'title': 'Test Task', 'due_at': '2024-06-30 23:59:59'}
        response = client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)

    def test_index_post_empty_title_sets_default(self):
        client = Client()
        data = {'title': '', 'due_at': '2024-06-30 23:59:59'}
        response = client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].title, '無題のタスク')

    def test_index_post_empty_title_and_due_sets_default(self):
        client = Client()
        data = {'title': '', 'due_at': ''}
        response = client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].title, '無題のタスク')
        self.assertIsNone(response.context['tasks'][0].due_at)

    def test_index_get_order_post(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task2)
        self.assertEqual(response.context['tasks'][1], task1)

    def test_index_get_order_due(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task1)
        self.assertEqual(response.context['tasks'][1], task2)


class ScrollToTopButtonTestCase(TestCase):
    """TOPボタン機能のテスト"""
    
    def test_scroll_to_top_button_exists(self):
        """TOPボタン要素がHTMLに存在するか確認"""
        client = Client()
        response = client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="scroll-to-top"')
    
    def test_scroll_to_top_button_has_correct_text(self):
        """TOPボタンが正しいテキストを持っているか確認"""
        client = Client()
        response = client.get('/')
        
        self.assertContains(response, '>TOP<')
    
    def test_scroll_to_top_button_links_to_top(self):
        """TOPボタンがページトップへのアンカーリンクであるか確認"""
        client = Client()
        response = client.get('/')
        
        self.assertContains(response, 'href="#top"')
    
    def test_page_has_top_anchor(self):
        """ページのトップにid='top'アンカーが存在するか確認"""
        client = Client()
        response = client.get('/')
        
        self.assertContains(response, 'id="top"')
    
    def test_css_scroll_to_top_button_style(self):
        """TOPボタンのスタイルシートが正しく含まれているか確認"""
        css_path = os.path.join(settings.BASE_DIR, 'todo', 'static', 'css', 'styles.css')
        with open(css_path, encoding='utf-8') as f:
            css_content = f.read()

        self.assertIn('.scroll-to-top', css_content)
        self.assertIn('position: fixed', css_content)
        self.assertIn('bottom: 20px', css_content)
        self.assertIn('right: 20px', css_content)

    def test_detail_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)

    def test_update_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/update'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/edit.html')
        self.assertEqual(response.context['task'], task)

    def test_update_post_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        data = {'title': 'Updated Task', 'due_at': '2024-08-01 00:00:00'}
        response = client.post('/{}/update'.format(task.pk), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/{}/'.format(task.pk))
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task')
        self.assertEqual(task.due_at, timezone.make_aware(datetime(2024, 8, 1, 0, 0, 0)))

    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')

        self.assertEqual(response.status_code, 404)

    def test_delete_success(self):
        task = Task(title='taskdel')
        task.save()
        client = Client()
        response = client.post('/{}/delete'.format(task.pk))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_fail(self):
        client = Client()
        response = client.post('/999/delete')

    def test_update_get_fail(self):
        client = Client()
        response = client.get('/1/update')
        self.assertEqual(response.status_code, 404)

    def test_close_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/close'.format(task.pk))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        task.refresh_from_db()
        self.assertTrue(task.completed)

    def test_close_fail(self):
        client = Client()
        response = client.get('/999/close')

        self.assertEqual(response.status_code, 404)
