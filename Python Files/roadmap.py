import win32com.client
from datetime import datetime, timedelta
from langchain_groq import ChatGroq  # type: ignore
from langchain_core.prompts import PromptTemplate  # type: ignore
import fitz  # type: ignore
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import time
