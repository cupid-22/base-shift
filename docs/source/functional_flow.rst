==============================
Functional Flow
==============================

This section outlines the functional flow of the system, detailing how different components interact and the overall user journey.

**User Journey:**

1. **Login and Authentication:**
   - Users authenticate through OAuth2.0/JWT.
   - API Gateway routes the requests to the appropriate microservice.

2. **Dashboard and Navigation:**
   - Post-login, users land on a customizable dashboard.
   - Navigation is facilitated through dynamically generated menus.

3. **Order Management (For POS):**
   - Users can create, view, and manage orders.
   - The system processes orders and communicates with backend microservices.

4. **Manufacturing Line Management:**
   - Orders trigger manufacturing processes.
   - Manufacturing lines are monitored and managed in real-time.

5. **Inventory Management:**
   - The system tracks inventory levels and updates as items are ordered or manufactured.
   - Notifications are sent when inventory levels are low.

6. **Analytics and Reporting:**
   - Users can view reports and analytics for decision-making.
   - Data is collected and processed through the backend and visualized on the frontend.

**Data Flow:**

- **Frontend:** React components handle user inputs.
- **Backend:** Microservices process requests, interact with databases, and perform business logic.
- **Database:** CRUD operations are managed, with data consistency ensured.
- **Event-Driven Architecture:** Kafka manages asynchronous tasks and event-driven workflows.

Refer to the architecture diagram for a visual representation of the data flow.

.. figure:: docs/source/_static/only_architecture.png
   :alt: Functional Flow Diagram

   Functional Flow Diagram
