<img src="static/readme-images/jr-catering-overall.png" alt="JR Catering Homepage" width="800"/>

# JR Catering Website

## Description
A full-stack restaurant booking and catering management system that allows users to create accounts, make reservations, and manage their bookings. The website also provides information about the catering services, menu options, and contact details.

## Table of Contents

1. [Description](#description)
2. [Features](#features)
   - [Homepage](#homepage)
   - [Menu Page](#menu-page)
   - [Booking System](#booking-system)
   - [User Authentication](#user-authentication)
   - [Contact Page](#contact-page)
   

3. [Technologies Used](#technologies-used)
   - [Frontend](#frontend)
   - [Backend](#backend)
   - [Deployment](#deployment)

4. [Installation & Setup](#installation--setup)
   - [Local Development](#local-development)
   - [Environment Variables](#environment-variables)
   - [Database Setup](#database-setup)

5. [Deployment](#deployment)
   - [Heroku Deployment](#heroku-deployment)
   - [Local Deployment](#local-deployment)
   - [Dependencies](#dependencies)

6. [Testing](#testing)
   - [Manual Testing](#manual-testing)
   - [Automated Testing](#automated-testing)
   - [Validation](#validation)

7. [Credits](#credits)
   - [Content](#content)
   - [Media](#media)
   - [Acknowledgments](#acknowledgments)

8. [Future Features](#future-features)

9. [Contact](#contact)

## Features
  - User Authentication (Register/Login)
  - Booking Management System
  - Create new bookings
  - Edit existing bookings
  - Cancel bookings  
  - View booking history
  - Real-time Booking Updates
  - Contact Form with Email Integration
  - Interactive Menu Display
  - Responsive Design for Mobile and Desktop
  - Admin Dashboard for Booking Management
  - View all bookings
  - Manage user accounts
  - Handle booking requests
  - Update menu items

### Homepage
The homepage welcomes users with:
- Clean, modern design
- Navigation menu for easy access to all sections
- Featured menu items
- About us section
- Call-to-action buttons for booking and contact
- Responsive design that works on all

### Booking System
Comprehensive booking management:
- User-friendly booking form
- Date and time selection
- Guest number specification
- Special requests field
- Real-time availability checking
- View existing bookings
- Edit booking functionality
- Cancel booking option
- Booking history

### User Authentication
Secure user account management:
- User registration
- Login system
- Password reset functionality
- Personal information storage
- Session management
- Security features

### Contact Page
Interactive contact features:
- Contact form with email integration
- Business hours display
- Location information
- Google Maps integration
- Phone and email contact options
- Social media links
- Direct messaging system

### Menu Page
Interactive menu display featuring:
- Categorized food sections
- Detailed descriptions of each dish
- Pricing information
- Special dietary indicators (Vegetarian, Vegan, Gluten-Free)
- High-quality food images
- Daily specials section

## Technologies Used- 
- Frontend:
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 

- Backend:
  - Python
  - Flask Framework
  - SQLAlchemy
  - SQLite Database

- Deployment:
  - Heroku 

## Installation & Setup
1. Clone the repository
2. Create a virtual environment
3. Install the required dependencies
4. Set up the database
5. Run the application


## Libraries and Tools
- Am I Responsive
- W3C Validator
- Font Awesome
- Google Fonts
- Git
- GitHub
- Heroku
- Gunicorn
- Pip
- Youtube
- Stack Overflow
- Google
- Chat GPT
- Reddit
- HTML Validator
- CSS Validator
- JSHint

## Bugs
### The time slot selection is not working as expected.
    I got this to work by using a select element instead of an input element.
### Database not updating
    I got this to work by adding a function to update the database when the form is submitted with debug statements to check where the error was coming from.


## Deployment

### Heroku Deployment
The site was deployed to Heroku. The steps to deploy are as follows:

1. Create a new Heroku app:
   - Log in to Heroku
   - Click "New" from the dashboard
   - Select "Create new app"
   - Enter a unique app name
   - Choose your region (EU or USA)
   - Click "Create app"

2. Set up environment variables:
   - From your app dashboard, click on "Settings"
   - Click "Reveal Config Vars"
   - Add the following config vars:
     - `SECRET_KEY`: Your secret key
     - `DATABASE_URL`: Your database URL
     - `CLOUDINARY_URL`: Your Cloudinary URL (if using Cloudinary)
     - `PORT`: 8000

3. Prepare the application:
   - In your GitHub repository, create a `requirements.txt`:
     ```
     pip freeze > requirements.txt
     ```
   - Create a `Procfile` in the root directory:
     ```
     web: gunicorn app:app
     ```

4. Connect to GitHub:
   - Go to the "Deploy" tab in your Heroku dashboard
   - Select "GitHub" as the deployment method
   - Connect to your GitHub repository
   - Choose the branch you want to deploy

5. Deploy:
   - Choose "Enable Automatic Deploys" for automatic deployment when you push to GitHub
   - Click "Deploy Branch" for manual deployment



## Usage
### User Features
- Register for an account or log in
- Navigate to the booking section to make a reservation
- View and manage your bookings in the bookings dashboard
- Use the contact form for inquiries
- Browse the menu and services offered

### Admin Features
- View all user bookings and manage them
- Update menu items and availability
- Handle user inquiries
- View booking statistics

## Testing
### Manual Testing
- User Authentication
- Registration
- Login
- Password Reset
- Booking System
- Creating Bookings
- Editing Bookings
- Cancelling Bookings
- Contact Form
- Responsive Design
- Admin Functions


## Manual Testing

Manual testing was conducted to ensure that all features of the JR Catering Website function as expected. Below are the details of the tests performed:

### User Authentication
- **Registration Form**: Tested by creating new user accounts with valid and invalid data to ensure proper validation and error handling.
- **Login Form**: Tested with correct and incorrect credentials to verify authentication and error messages.
- **Password Reset**: Verified the password reset process, including email notifications and form validation.

### Booking System
- **Create Booking**: Tested the booking form by entering valid and invalid data, ensuring that bookings are created and stored correctly.
- **Edit Booking**: Verified that existing bookings can be edited, with changes saved and reflected in the booking history.
- **Cancel Booking**: Tested the cancellation process to ensure bookings are removed from the system and the user is notified.

### Contact Form
- **Form Submission**: Tested the contact form with valid and invalid inputs to ensure messages are sent and error messages are displayed when necessary.
- **Email Integration**: Verified that emails are sent to the correct address upon form submission.

### Menu Page
- **Navigation**: Ensured that all menu items are displayed correctly and that navigation between categories is smooth.
- **Special Dietary Indicators**: Checked that indicators for vegetarian, vegan, and gluten-free options are displayed correctly.

### Responsive Design
- **Mobile and Desktop Views**: Tested the website on various devices and screen sizes to ensure a responsive design and proper layout.
- **Navigation Menu**: Verified that the navigation menu is accessible and functional on all devices.

### Admin Functions
- **Booking Management**: Tested the admin dashboard for viewing, editing, and deleting user bookings.
- **User Management**: Verified that admin can manage user accounts, including viewing and editing user details.
- **Menu Updates**: Ensured that menu items can be updated and changes are reflected on the user-facing menu page.

### General UI/UX
- **Button Functionality**: Tested all buttons to ensure they perform the expected actions, such as submitting forms, navigating pages, and opening modals.
- **Form Validation**: Verified that all forms have appropriate validation and error messages for required fields and incorrect inputs.
- **Feedback Messages**: Checked that users receive appropriate feedback messages for actions like booking creation, cancellation, and form submissions.

These tests were conducted to ensure a smooth and error-free user experience across all features of the JR Catering Website.


### CSS
- W3C Validator

<img src="static/readme-images/jr-catering-css.png" alt="JR Catering CSS" width="800"/>

## Future Features
- Online payment integration
- SMS notifications
- Table layout visualization
- Customer review system

## Credits
- Mentor: [Mo Shami]
- Code Institute
