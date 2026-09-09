Technology Stack: Python, Django, Django REST Framework
Scenario
Build the backend for QuickBook, an event booking platform where customers can browse
events, book tickets, and register using a referral code. The application should expose REST
APIs, maintain booking consistency, and include a custom staff dashboard.

Follow Django best practices and organize the project using a clean and maintainable
architecture.
1. Authentication
User Registration
User Login
User Logout
Token-based authentication
Protected APIs

2. Event Booking
Implement the complete event booking workflow.

Customers should be able to:
Browse events
View event details
Search and filter events
Book tickets
Cancel bookings
View their booking history

Requirements:
Proper validation
Accurate seat availability
Prevention of invalid bookings
Correct behaviour under concurrent booking requests
Reusable business logic
Proper HTTP status codes and error responses

3. Binary Referral Network
Each registered user should receive a unique referral code that can be used during
registration.

The referral system should support:
Registering users using a referral code
Automatic placement within the referral network
Retrieving a user&#39;s referral tree
Retrieving the root user of a referral tree
Returning left and right referral team counts
Proper validation and error handling

Required APIs:
POST /api/auth/register/
GET /api/referrals/&lt;user_id&gt;/tree/
GET /api/referrals/&lt;user_id&gt;/root/
GET /api/referrals/&lt;user_id&gt;/stats/

4. Custom Staff Dashboard
Do not use Django&#39;s built-in Admin panel.

Only staff users should be able to access the dashboard.

Dashboard:
Total Customers
Total Vendors
Total Events
Total Bookings

Vendor Management:
Add Vendor
View Vendors
Update Vendor Information

Event Management:
Add Events
View Events
Update Events
Search and Filter Events

User Management:
View Users
User Information (detailed page)
User referral tree view with search (In detailed page)

Dashboard Requirements:
Staff authentication
Search
Pagination
Responsive layout
Proper access control

5. Bonus
Swagger / OpenAPI Documentation
API Rate Limiting

General Requirements
Follow Django best practices.
Use a clean and modular project structure.
Keep business logic separate from views.
Follow REST API conventions.
Implement proper validation and exception handling.
Write clean, maintainable, and well-documented code.

Submission
Use SQLite Database
Add requirements.txt
Share GitHub repo with README.md