
from django.test import TestCase


from django.contrib.auth.models import Permission # Required to grant the permission needed to set a book as returned.

class RenewBookInstancesViewTest(TestCase):

	def setUp(self):
		#Create a user
		test_user1 = User.objects.create_user(username='testuser1', password='12345')
		test_user1.save()

		test_user2 = User.objects.create_user(username='testuser2', password='12345')
		test_user2.save()
		permission = Permission.objects.get(name='Set book as returned')
		test_user2.user_permissions.add(permission)
		test_user2.save()

		#Create a book
		test_author = Author.objects.create(first_name='John', last_name='Smith')
		test_genre = Genre.objects.create(name='Fantasy')
		test_language = Language.objects.create(name='English')
		test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=test_author, language=test_language,)
		# Create genre as a post-step
		genre_objects_for_book = Genre.objects.all()
		test_book.genre=genre_objects_for_book
		test_book.save()

		#Create a BookInstance object for test_user1
		return_date= datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance1=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user1, status='o')

		#Create a BookInstance object for test_user2
		return_date= datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance2=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user2, status='o')
		

	def test_redirect_if_not_logged_in(self):
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		#Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
		self.assertEqual( resp.status_code,302)
		self.assertTrue( resp.url.startswith('/accounts/login/') )
		
	def test_redirect_if_logged_in_but_not_correct_permission(self):
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		
		#Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
		self.assertEqual( resp.status_code,302)
		self.assertTrue( resp.url.startswith('/accounts/login/') )

	def test_logged_in_with_permission_borrowed_book(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance2.pk,}) )
		
		#Check that it lets us login - this is our book and we have the right permissions.
		self.assertEqual( resp.status_code,200)

	def test_logged_in_with_permission_another_users_borrowed_book(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		
		#Check that it lets us login. We're a librarian, so we can view any users book
		self.assertEqual( resp.status_code,200)

	def test_HTTP404_for_invalid_book_if_logged_in(self):
		import uuid 
		test_uid = uuid.uuid4() #unlikely UID to match our bookinstance!
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid,}) )
		self.assertEqual( resp.status_code,404)
		
	def test_uses_correct_template(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		self.assertEqual( resp.status_code,200)

		#Check we used correct template
		self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')
		
		
