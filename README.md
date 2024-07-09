LIBRARY

****Requirements:****

**Functional (what the system should do):**
Web-based
1. Manage books inventory
2. Manage books borrowing
3. Manage customers
4. Display notifications
5. Handle payments

**Non-functional (what the system should deal with):**
1. Support for 5 concurrent users
2. Handle up to 1000 books
3. Support 50,000 borrowings per year
4. Approximate data usage of ~30MB per year

****Specific Endpoint Requirements:****
**Payment Endpoint:**

*Implement an endpoint that makes requests to the Stripe service to handle payments.*

**Borrowers List Endpoint:**

*Endpoint takes a search string as an argument and returns a list of current borrowers.*

**Local Database Integration:**

*Requests of the implemented API should work with the local database (fetch data from the database, not from the Library API)*


****Technologies to Use:****
* Stripe API: Stripe API Documentation
* Telegram API: Telegram API Documentation
* Celery Beat:
- Use Celery Beat as a task scheduler to check all overdue borrowers.
* Celery for Asynchronous Requests:
- Use Celery to make asynchronous requests to Telegram to notify about each new borrower.
* Swagger Documentation:
- All endpoints should be documented via Swagger.

****How to Run:****

1. Copy .env.sample to .env and populate it with all required data.
2. Run the following command to build and start the application:

`docker-compose up --build`

3. Create an admin user and schedule the synchronization of overdue borrowers.
