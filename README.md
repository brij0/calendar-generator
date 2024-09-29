# University Course Calendar Automation System

[![License](https://img.shields.io/static/v1?label=License&message=MIT&color=blue&style=plastic&logo=appveyor)](https://opensource.org/licenses/MIT)

## Table Of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [GitHub](#github)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)
- [Tests](#tests)
- [License](#license)

![GitHub repo size](https://img.shields.io/github/repo-size/brij0/University-Course-Calendar-Automation?style=plastic)
![GitHub top language](https://img.shields.io/github/languages/top/brij0/University-Course-Calendar-Automation?style=plastic)

## Description

This project automates the extraction and integration of academic events (like lectures, labs, exams, etc.) from course outlines into a user's Outlook calendar. It uses LLM (LLaMA 3.1) to parse PDF course outlines and then pushes the extracted events to the user's Outlook calendar. The events include details such as dates, times, locations, and descriptions. This system aims to save students time by eliminating the need to manually add academic events to their calendars.

### Key Features:
- **Automated event extraction** from PDF course outlines.
- **Calendar Integration**: Automatically adds events (e.g., lectures, exams, assignments) to the Outlook calendar.
- **Handles multiple PDFs**: Processes all PDFs in a specified folder.
- **Real-time updates**: Detects any missing or TBA details and processes them accordingly.

## Installation

To run this project locally, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/brij0/University-Course-Calendar-Automation.git
    ```

2. **Navigate to the project directory**:
    ```bash
    cd University-Course-Calendar-Automation
    ```

3. **Set up a virtual environment** (optional but recommended):
    ```bash
    python -m venv env
    source env/bin/activate   # On Windows: env\Scripts\activate
    ```

4. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Download the necessary LLaMA 3.1 model** and configure the environment variable for the API key (`GROQ_API_KEY`). Save the models in the `/models` folder.

6. **Run the system**:
    ```bash
    python calendar_automation.py
    ```

## Usage

1. Once the system is running, it will automatically scan the PDFs in the specified folder for course outlines.
2. The system parses the PDFs using LLaMA 3.1 and extracts all important academic events.
3. All extracted events will be added to your Outlook calendar, including details such as event type (Lecture, Lab, Exam), date, time, location, and description.
   
### Example Workflow:

- **Admin uploads PDF course outlines** into the designated folder.
- **System processes** the PDFs and extracts all events like lectures, exams, and assignments.
- **Events are added to the Outlook calendar** with all relevant details (time, date, location, etc.).


## Contributing

Contributions to this project are welcome! Follow these steps:

1. Fork the repository.
2. Create a new feature branch: `git checkout -b feature-branch`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-branch`.
5. Submit a pull request.

Please ensure that your code follows best practices and is well documented.

## GitHub

You can find the repository and more projects at my GitHub profile:

- brij0's [GitHub Profile](https://github.com/brij0/)

## Contact

Feel free to reach out for any questions, feedback, or collaborations:

- Email: bthakrar@uoguelph.ca

## Acknowledgements

Special thanks to the following resources and individuals for their help and support throughout this project:

- **YouTube Tutorials**: The following YouTube tutorials were invaluable in guiding the development of this project:
  - [Working with PDF files in Python](https://www.youtube.com/watch?v=mrj6wYp94FE)
  - [Python Outlook Automation](https://www.youtube.com/watch?v=GURxCmKzmDc)

- **Friends**: A huge thanks to my friends for their help and feedback during the project. Check out their GitHub profiles:
  - [Denil Dubariya](https://github.com/denildubariya18)
  - [Jay Agrawat](https://github.com/JayAgravat1092)

- **LangChain and Groq**: A special mention to LangChain and Groq for providing the LLaMA 3.1 integration capabilities.

## Tests

To run the tests, you can use the following command:

```bash
pytest
