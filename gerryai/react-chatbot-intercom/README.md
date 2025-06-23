# React Chatbot Intercom

This project is a React-based chatbot and intercom system that utilizes Firebase as its backend. It supports voice input, displays a HUD with recent queries and answers, and can show images and videos. Additionally, it functions as a home intercom system between tablets.

## Features

- **Chat Functionality**: Users can send and receive messages in real-time.
- **Voice Input**: Users can send messages using voice commands.
- **HUD Display**: Recent queries and answers are displayed for quick reference.
- **Media Support**: The application can display images and play videos.
- **Intercom System**: Connect and communicate between tablets in the home.

## Project Structure

```
react-chatbot-intercom
├── src
│   ├── components
│   │   ├── Chat
│   │   ├── HUD
│   │   ├── Media
│   │   ├── Intercom
│   │   └── common
│   ├── hooks
│   ├── services
│   ├── types
│   ├── utils
│   ├── App.tsx
│   ├── App.css
│   └── index.tsx
├── public
│   └── index.html
├── package.json
├── tsconfig.json
├── firebase.json
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd react-chatbot-intercom
   ```
3. Install the dependencies:
   ```
   npm install
   ```

## Usage

To start the application, run:
```
npm start
```
This will launch the application in your default web browser.

## Firebase Setup

Make sure to set up Firebase for your project. You will need to create a Firebase project and configure the necessary authentication and database settings. Update the `src/services/firebase.ts` file with your Firebase configuration.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.