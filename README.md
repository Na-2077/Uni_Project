# Uni_Project
## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Na-2077/Uni_Project
   cd Uni_Project
   ```

2. **Create and activate a virtual environment (recommended)**

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API key**

   - Create a `.env` file in the project root:
     ```
     OPENAI_API_KEY=your-openai-key-here
     ```

5. **(Optional) Add PedramBot.ico**
   - Place `PedramBot.ico` file in the project directory for a custom window icon.

## Usage

Run the application:

```bash
python pedrambot.py
```

- Enter the PIN code (default: `123123`) to access the chatbot.
- Start chatting!

## Project Structure

- `Main.py`: Main application file (you can rename as you wish).
- `chat_history.json`: Automatically created for saving chat history.
- `.env`: Your API key (not shared or committed).

## License

*(Specify your license here, e.g., MIT or Apache 2.0)*

## Author

Pedram
