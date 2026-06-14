# Use Case Diagram: MediPredict AI

The application defines two principal actors: the **Patient/User** and the **System Administrator**.

## Use Case Diagram

```mermaid
left-to-right-direction
actor Patient
actor Administrator

rectangle MediPredict_System {
    usecase "Register & Login" as UC_Auth
    usecase "Run Health Screenings" as UC_Predict
    usecase "View Personal History" as UC_History
    usecase "Search & Filter Records" as UC_Search
    usecase "Download PDF Assessment" as UC_PDF
    usecase "Email Report to Doctor" as UC_Email
    usecase "Toggle Dark Mode" as UC_Theme
    
    usecase "View Admin Dashboard" as UC_Admin_Dash
    usecase "Compare ML Model Metrics" as UC_Admin_ML
    usecase "Monitor Users & Logs" as UC_Admin_Users
}

Patient --> UC_Auth
Patient --> UC_Predict
Patient --> UC_History
Patient --> UC_Search
Patient --> UC_PDF
Patient --> UC_Email
Patient --> UC_Theme

Administrator --> UC_Auth
Administrator --> UC_Admin_Dash
Administrator --> UC_Admin_ML
Administrator --> UC_Admin_Users
Administrator --> UC_Theme
```

## Actor Actions Breakdown

### 1. Patient/User
- **Authentication**: Registers an account with a unique username and email, and authenticates via the login interface.
- **Risk Screenings**: Selects a disease module (Diabetes, Heart, Kidney), enters clinical vitals, and submits data to run predictions.
- **Reporting**: Inspects results page with custom dials, downloads a PDF copy of their results, or emails the report via SMTP.
- **Timelines**: Views historical prediction lists, searches outcomes, and tracks personal trends on the dashboard.

### 2. Administrator
- **Oversight**: Logs into the admin dashboard to inspect all registered accounts, patient counts, and global prediction volume.
- **Model Evaluation**: Audits classification metrics (Accuracy, Precision, Recall, F1) and checks confusion matrices to monitor calibration.
