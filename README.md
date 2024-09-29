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


![GitHub repo size](https://img.shields.io/github/repo-size/brij0/calendar-generator?style=plastic)
![GitHub top language](https://img.shields.io/github/languages/top/brij0/calendar-generator?style=plastic)

## Description
This project is a real-time University Course Calendar Automation System that I whipped up in just **6 hours** with a little help from ChatGPT, YouTube, and, of course, my over-caffeinated brain. What started as a simple attempt to make my life easier by automatically adding academic events from course outlines to my Outlook calendar quickly spiraled into a much more "interesting" (read: complicated) project.

### Challenges Faced:
- **Inconsistent LLaMA 3 Output**: One of the biggest issues I faced is that LLaMA 3 doesn’t always provide consistent output. Since course outlines often contain vague or incomplete information (e.g., "Assignment due after every lab section"), the system struggles to extract precise dates without further context, such as a student's specific lab schedule.
- **Missing or Incomplete Information**: Many course outlines leave key details like dates, times, or locations as "TBA," and this causes issues when trying to add events to the Outlook calendar. If any of these fields are missing, the event cannot be properly created in the calendar.
- **PDF Parsing Difficulties**: Parsing the text from PDFs was also a challenge, as the formatting varies widely between course outlines. Some outlines are well-structured, while others are more difficult to process programmatically.
  
By no means is this system perfect. In fact, its functionality relies heavily on how well the course outlines are structured and whether all necessary information is provided explicitly. The LLM (LLaMA 3) does its best to infer missing details, but it's not foolproof, especially when crucial context is missing or vague in the original document. This can lead to incomplete or incorrect calendar events being added.

Despite these challenges, I am actively looking for solutions—so if anyone has any ideas for making this system more robust or can suggest a better prompt to get the best out of a course outline, I’m all ears. I’m even open to totally new solutions (though I’ll hate you for a while, but then I’ll be fine).

### Key Features:
- **Automated event extraction** from PDF course outlines.
- **Calendar Integration**: Automatically adds events (e.g., lectures, exams, assignments) to the Outlook calendar.
- **Handles multiple PDFs**: Processes all PDFs in a specified folder.
- **Real-time updates**: Detects any missing or TBA details and processes them accordingly.

## Installation

To run this project locally, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/brij0/calendar-generator.git
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
  - [Working with PDF files in Python by NeuralNine](https://www.youtube.com/watch?v=w2r2Bg42UPY)
  - [Using Llama with groq cloud by codebasics](https://www.youtube.com/watch?v=CO4E_9V6li0)

- **LangChain and Groq**: A special mention to LangChain and Groq for providing the LLaMA 3.1 integration capabilities.

## Tests

To run the tests, you can use the following command:

```bash
pytest
