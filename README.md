# Voice Assistant - Full Stack Application

A modern, fully-featured voice-controlled assistant with web interface and MySQL database integration.

## Features

✨ **Voice Recognition** - Real-time speech-to-text conversion
🗣️ **Smart Responses** - AI-powered command processing
💾 **Command History** - Save and retrieve all commands
🌐 **Web Interface** - Modern, responsive UI
🗄️ **Database** - MySQL integration for persistence
📱 **Mobile Friendly** - Works on desktop and mobile devices

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- MySQL Server installed and running
- Git (optional)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup (Optional)
If you want to use the database features:

1. Create a MySQL database:
```sql
CREATE DATABASE voice_assistant;
```

2. Update `.env` file with your database credentials

### 4. Environment Variables
Create or update `.env` file:
```
PORT=5000
DEBUG=True
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=voice_assistant
```

### 5. Run the Application
```bash
python voice.py
```

The assistant will start on `http://localhost:5000`

## Usage

1. **Open the Web Interface**: Navigate to `http://localhost:5000`
2. **Click Microphone Button**: Start the voice recognition
3. **Speak a Command**: Try commands like:
   - "What time is it?"
   - "What's today's date?"
   - "Who is Albert Einstein?"
   - "Open Google"
   - "Play music"
   - "Search Python tutorials"

## File Structure
```
voice_assistant/
├── voice.py              # Flask web app & main logic
├── assistant.py          # Legacy CLI assistant (optional)
├── database.py           # Database connection & operations
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── templates/
│   └── index.html       # Web interface
└── README.md            # This file
```

## Supported Commands

### Information
- Time and Date queries
- Wikipedia searches
- General knowledge questions

### Websites
- Open major websites (Google, YouTube, Facebook, etc.)
- Search Google
- Play YouTube videos

### System
- Help information
- Command history

## API Endpoints

### Process Command
- **POST** `/api/process`
- Body: `{"command": "your command"}`
- Response: `{"success": true, "response": "...", "command": "..."}`

### Get History
- **GET** `/api/history?limit=10`
- Response: `{"success": true, "history": [...]}`

## Troubleshooting

### Database Connection Issues
- Ensure MySQL is running
- Check credentials in `.env` file
- Verify database exists

### Microphone Issues
- Check browser microphone permissions
- Ensure no other app is using the microphone
- Try refreshing the page

### Recognition Issues
- Speak clearly and at normal pace
- Ensure good ambient sound levels
- Try shorter, simpler commands

## Requirements
- Flask==2.3.0
- mysql-connector-python==8.0.33
- SpeechRecognition==3.10.0
- gTTS==2.3.2
- wikipedia==1.4.0
- python-dotenv==1.0.0

## License
MIT License - Feel free to use and modify

## Future Enhancements
- [ ] Voice output (text-to-speech)
- [ ] Multiple language support
- [ ] Machine learning for command prediction
- [ ] Calendar integration
- [ ] Weather API integration
- [ ] User authentication
- [ ] Mobile app
